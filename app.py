import streamlit as st
import pandas as pd
import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document
import plotly.express as px


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Job Market Skill Analyzer",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD MARKET DATA
# =========================================================

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "processed" / "role_skill_demand.csv"

market_data = pd.read_csv(DATA_PATH)

market_data["skill_name"] = market_data["skill_name"].astype(str)
market_data["role_category"] = market_data["role_category"].astype(str)


# =========================================================
# RESUME TEXT EXTRACTION
# =========================================================

def extract_pdf_text(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(file):
    document = Document(file)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    return text


def extract_resume_text(uploaded_file):

    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_pdf_text(uploaded_file)

    elif uploaded_file.name.lower().endswith(".docx"):
        return extract_docx_text(uploaded_file)

    return ""


# =========================================================
# SKILL EXTRACTION
# =========================================================

def extract_skills(text, skills):

    text_lower = text.lower()

    detected = []

    for skill in skills:

        skill_lower = skill.lower().strip()

        if not skill_lower:
            continue

        # Special handling for single-letter R
        if skill_lower == "r":
            patterns = [
                r"\br programming\b",
                r"\br language\b",
                r"\br studio\b",
                r"\br\b"
            ]
        else:
            escaped_skill = re.escape(skill_lower)

            patterns = [
                rf"(?<!\w){escaped_skill}(?!\w)"
            ]

        for pattern in patterns:

            if re.search(pattern, text_lower):
                detected.append(skill)
                break

    return sorted(set(detected))


# =========================================================
# ROLE DETECTION
# =========================================================

def detect_role(detected_skills):

    roles = market_data["role_category"].unique()

    scores = {}

    for role in roles:

        role_data = market_data[
            market_data["role_category"] == role
        ]

        # Use the top 20 skills for each role
        top_skills = set(
            role_data
            .sort_values(
                "demand_percentage",
                ascending=False
            )
            .head(20)["skill_name"]
        )

        matches = len(
            set(detected_skills) & top_skills
        )

        scores[role] = matches

    if max(scores.values()) == 0:
        return "Unknown", scores

    detected_role = max(
        scores,
        key=scores.get
    )

    return detected_role, scores


# =========================================================
# HEADER
# =========================================================

st.title("📊 Job Market Skill-Demand Analyzer")

st.markdown(
    """
### Upload your resume and compare your skills with real job-market demand.

The system extracts technical skills from your resume and compares them
with skills demanded across **AI/ML, Data Analytics, and Software Development** roles.
"""
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Analysis Settings")

role_option = st.sidebar.selectbox(
    "Choose role",
    [
        "Auto Detect",
        "AI/ML",
        "Data Analytics",
        "Software Development"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Upload a PDF or DOCX resume to begin the analysis."
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📄 Upload your resume",
    type=["pdf", "docx"]
)


if uploaded_file:

    # Extract text
    resume_text = extract_resume_text(uploaded_file)

    if not resume_text.strip():

        st.error(
            "Could not extract text from this resume. "
            "Please upload a text-based PDF or DOCX."
        )

    else:

        # Extract skills
        all_skills = market_data["skill_name"].unique()

        detected_skills = extract_skills(
            resume_text,
            all_skills
        )

        # Detect role
        detected_role, role_scores = detect_role(
            detected_skills
        )

        # Manual role selection overrides automatic detection
        if role_option != "Auto Detect":
            selected_role = role_option
        else:
            selected_role = detected_role


        # =====================================================
        # ROLE SECTION
        # =====================================================

        st.subheader("🎯 Resume Analysis")

        if selected_role == "Unknown":

            st.warning(
                "We could not confidently detect a role from the extracted skills. "
                "Please select a role from the sidebar."
            )

        else:

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Detected / Selected Role",
                    selected_role
                )

            with col2:
                st.metric(
                    "Skills Detected",
                    len(detected_skills)
                )

            with col3:
                role_jobs = (
                    market_data[
                        market_data["role_category"] == selected_role
                    ]["total_jobs"]
                    .iloc[0]
                )

                st.metric(
                    "Jobs Analyzed",
                    int(role_jobs)
                )


            # =================================================
            # DETECTED SKILLS
            # =================================================

            st.subheader("✅ Skills Found in Your Resume")

            if detected_skills:

                skill_text = " • ".join(
                    detected_skills
                )

                st.success(skill_text)

            else:

                st.warning(
                    "No matching technical skills were detected."
                )


            # =================================================
            # MARKET ANALYSIS
            # =================================================

            role_data = market_data[
                market_data["role_category"] == selected_role
            ].copy()

            role_data = role_data.sort_values(
                "demand_percentage",
                ascending=False
            )


            # =================================================
            # SKILL COMPARISON
            # =================================================

            role_data["In Resume"] = role_data[
                "skill_name"
            ].isin(detected_skills)


            st.subheader(
                "📈 Your Skills vs Job-Market Demand"
            )

            comparison = role_data[
                [
                    "skill_name",
                    "job_count",
                    "total_jobs",
                    "demand_percentage",
                    "In Resume"
                ]
            ].head(15)

            comparison = comparison.rename(
                columns={
                    "skill_name": "Skill",
                    "job_count": "Jobs Requiring Skill",
                    "total_jobs": "Total Jobs",
                    "demand_percentage": "Market Demand %",
                }
            )

            comparison["Market Demand %"] = (
                comparison["Market Demand %"]
                .round(2)
            )

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # TOP MARKET SKILLS
            # =================================================

            st.subheader(
                f"🔥 Top Skills in {selected_role}"
            )

            top_skills = role_data.head(10).copy()

            fig = px.bar(
                top_skills.sort_values(
                    "demand_percentage"
                ),
                x="demand_percentage",
                y="skill_name",
                orientation="h",
                labels={
                    "demand_percentage": "Market Demand (%)",
                    "skill_name": "Skill"
                },
                title=f"Top 10 Skills — {selected_role}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            # =================================================
            # SKILL GAP
            # =================================================

            st.subheader("⚠️ Your Skill Gap")

            missing_skills = role_data[
                ~role_data["skill_name"].isin(
                    detected_skills
                )
            ].head(10).copy()

            if len(missing_skills) > 0:

                missing_display = missing_skills[
                    [
                        "skill_name",
                        "job_count",
                        "demand_percentage"
                    ]
                ].rename(
                    columns={
                        "skill_name": "Missing Skill",
                        "job_count": "Jobs Requiring It",
                        "demand_percentage": "Market Demand %"
                    }
                )

                missing_display[
                    "Market Demand %"
                ] = missing_display[
                    "Market Demand %"
                ].round(2)

                st.dataframe(
                    missing_display,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No major missing skills were identified "
                    "from the analyzed market skills."
                )


            # =================================================
            # SIMPLE SUMMARY
            # =================================================

            st.subheader("📝 Analysis Summary")

            matched_count = len(
                set(detected_skills)
                & set(role_data["skill_name"])
            )

            total_market_skills = len(role_data)

            st.write(
                f"""
                Your resume contains **{matched_count}**
                skills that appear in our analyzed job-market skill set
                for **{selected_role}**.

                The comparison is based on **{int(role_jobs):,}**
                job postings in this role category.

                The skill-gap section highlights market-demand skills
                that were not detected in your uploaded resume.
                """
            )

else:

    st.info(
        "👆 Upload your resume above to start the analysis."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "NLP-based Job Market Skill-Demand Analyzer | "
    "Built using Python, Pandas, Streamlit and Plotly"
)