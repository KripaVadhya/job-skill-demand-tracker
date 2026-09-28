# Job Market Skill Demand Analyzer

An end-to-end data analytics and NLP project that analyzes job-market skill demand and compares an individual's resume with market requirements.

## Project Overview

This project analyzes job postings to identify the technical skills demanded across three major technology roles:

- AI/ML
- Data Analytics
- Software Development

It also includes a Streamlit Resume Skill Analyzer that compares a candidate's skills with market demand and identifies potential skill gaps.

## Key Results

| Metric | Value |
|---|---:|
| Raw job postings | 123,849 |
| Relevant jobs analyzed | 2,358 |
| Technical skill records | 11,881 |
| AI/ML jobs | 385 |
| Data Analytics jobs | 412 |
| Software Development jobs | 1,561 |

## Project Pipeline

Raw Job Postings  
↓  
Data Cleaning  
↓  
Relevant Job Filtering  
↓  
Role Classification  
↓  
Technical Skill Extraction  
↓  
Skill Demand Analysis  
↓  
Power BI Dashboard  
↓  
Resume Skill Extraction  
↓  
Market Comparison  
↓  
Skill Gap Analysis

## Power BI Dashboard

The Power BI dashboard provides:

- Total jobs analyzed
- Job distribution by role
- Top 10 skills by market demand
- Role-based filtering
- Role-wise job demand

Dashboard file:

`dashboard/Job_Skill_Demand_Analyzer.pbix`

## Resume Skill Analyzer

The Streamlit application allows users to upload a PDF or DOCX resume.

The application:

1. Extracts resume text
2. Detects technical skills
3. Detects/selects the relevant role
4. Compares resume skills with market demand
5. Identifies missing skills
6. Displays a skill-gap summary

## Validation

A manually validated sample of 41 extracted skill matches was evaluated.

- Correct matches: 38
- Incorrect matches: 3
- Precision: 92.68%

This precision is based on the manually validated sample.

## Tech Stack

- Python
- Pandas
- Regular Expressions
- Streamlit
- Plotly
- Power BI
- SQL / MySQL

## Project Structure

```text
Job-Skill Demand Tracker/
│
├── app.py
├── dashboard/
│   └── Job_Skill_Demand_Analyzer.pbix
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── sql/
├── src/
├── README.md
├── requirements.txt
└── .gitignore