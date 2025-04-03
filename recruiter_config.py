import streamlit as st
import os
import uuid
import json
from datetime import datetime

# Setup
st.set_page_config(page_title="Recruiter Job Config", layout="centered")
st.title("🧑‍💼 Create a Job Posting")

# File system setup
DATA_DIR = "job_configs"
os.makedirs(DATA_DIR, exist_ok=True)

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
        "Skills/Experience Match",
        "Salary Expectation",
        "Notice Period",
        "Optional (Text)"
    ], key=f"q{i}_type")
    response_type = st.selectbox("Expected Response Type", ["Text", "Yes/No", "Number"], key=f"q{i}_resp")
    disqualify_if_no = False
    if response_type == "Yes/No":
        disqualify_if_no = st.checkbox("Disqualify if answered 'No'?", key=f"q{i}_disq")
    salary_range = ""
    if q_type == "Salary Expectation":
        salary_range = st.text_input("Expected Salary Range (e.g. 8000-12000)", key=f"q{i}_range")

    if q_text:
        questions.append({
            "question": q_text,
            "type": q_type,
            "response_type": response_type,
            "disqualify_if_no": disqualify_if_no,
            "salary_range": salary_range
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

        # 🎯 Candidate form link
        candidate_form_url = f"https://your-candidate-app.streamlit.app/?job_id={job_id}"
        st.markdown(f"**🔗 Candidate Application Link:** [Click to Copy]({candidate_form_url})")
        st.code(candidate_form_url, language="text")
