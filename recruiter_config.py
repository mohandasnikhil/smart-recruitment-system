import streamlit as st
import pandas as pd
import os
import uuid
import json
from datetime import datetime

# Setup
st.set_page_config(page_title="Recruiter Job Config", layout="centered")
st.title("🧑‍💼 Create a Job Posting")

# File system setup
DATA_DIR = "job_configs"
RESPONSES_DIR = "job_responses"
RESUMES_DIR = "resumes"

for folder in [DATA_DIR, RESPONSES_DIR, RESUMES_DIR]:
    os.makedirs(folder, exist_ok=True)

# Step 1: Upload Job Description
st.subheader("1. Upload Job Description")
jd_text = st.text_area("Paste the job description here", height=200)

# Step 2: Define Screening Questions
st.subheader("2. Define Up to 6 Screening Questions")
questions = []
for i in range(6):
    st.markdown(f"**Question {i+1}**")
    q_text = st.text_input(f"Question {i+1} Text", key=f"q{i}_text")
    q_type = st.selectbox("Question Type", [
        "Mandatory (Yes/No)",
        "Skills/Experience Match",
        "Salary Expectation",
        "Notice Period",
        "Optional (Text)",
        "---"
    ], key=f"q{i}_type")
    expected_salary_range = ""
    if q_type == "Salary Expectation":
        expected_salary_range = st.text_input("Expected Salary Range (e.g. 8000-12000)", key=f"q{i}_range")
    if q_text:
        questions.append({
            "question": q_text,
            "type": q_type,
            "salary_range": expected_salary_range
        })

# Step 3: Save Job Posting
st.subheader("3. Save Job Posting")
if st.button("✅ Save Job"):
    if not jd_text or not questions:
        st.warning("Please provide a job description and at least one question.")
    else:
        job_id = str(uuid.uuid4())[:8]
        config = {
            "job_id": job_id,
            "created_at": str(datetime.now()),
            "job_description": jd_text,
            "questions": questions
        }
        with open(f"{DATA_DIR}/{job_id}.json", "w") as f:
            json.dump(config, f, indent=2)
        st.success(f"✅ Job saved successfully with ID: {job_id}")
        st.code(f"Job ID: {job_id}", language="text")

