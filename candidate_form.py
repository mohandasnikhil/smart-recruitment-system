import streamlit as st
import os
import json
import uuid
import pandas as pd
from datetime import datetime
import re

# --- Setup ---
st.set_page_config(page_title="Apply for a Job", layout="centered")
st.title("📄 Job Application Form")

# --- Paths ---
CONFIG_DIR = "job_configs"
RESPONSES_DIR = "job_responses"
RESUMES_DIR = "resumes"

os.makedirs(RESPONSES_DIR, exist_ok=True)
os.makedirs(RESUMES_DIR, exist_ok=True)

# --- Step 1: Get job_id from query params if present ---
query_params = st.experimental_get_query_params()
preselected_job_id = query_params.get("job_id", [None])[0]

# --- Step 2: Load job config ---
job_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

if preselected_job_id:
    job_file = f"{preselected_job_id}.json"
    if job_file not in job_files:
        st.error("❌ Invalid job link or job not found.")
        st.stop()
else:
    if not job_files:
        st.error("No job configurations found. Please check with the recruiter.")
        st.stop()
    job_file = st.selectbox("Select the Job you are applying for:", job_files)

with open(os.path.join(CONFIG_DIR, job_file), "r") as f:
    job_config = json.load(f)

st.subheader("📝 Job Description")
st.markdown(job_config["job_description"])

# --- Step 3: Collect Candidate Info ---
st.subheader("👤 Your Information")
name = st.text_input("Your Full Name")
email = st.text_input("Your Email Address")
phone = st.text_input("Phone Number (include country code, e.g. +971501234567)")
linkedin = st.text_input("LinkedIn Profile URL (optional)")

# --- Validation ---
def is_valid_email(e):
    return "@" in e and "." in e

def is_valid_phone(p):
    return bool(re.match(r"^\+?\d{7,15}$", p))

# --- Step 4: Show Questions and Resume Upload ---
if name and is_valid_email(email) and is_valid_phone(phone):
    st.subheader("🧠 Answer the Screening Questions")
    answers = []
    disqualified = False

    for i, q in enumerate(job_config["questions"]):
        q_text = q["question"]
        q_type = q.get("type", "Optional (Text)")
        response_type = q.get("response_type", "Text")
        disqualify_if_no = q.get("disqualify_if_no", False)

        if response_type == "Yes/No":
            answer = st.radio(q_text, ["Yes", "No"], key=f"q_{i}")
            if disqualify_if_no and answer == "No":
                disqualified = True
        elif response_type == "Number":
            answer = st.number_input(q_text, min_value=0, step=1, key=f"q_{i}")
        else:
            answer = st.text_input(q_text, key=f"q_{i}")

        answers.append(answer)

    st.subheader("📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    # --- Step 5: Submit ---
    st.subheader("✅ Submit Application")
    if st.button("Submit Application"):
        if not uploaded_file or not all(str(a).strip() for a in answers):
            st.warning("Please fill out all fields and upload your resume.")
        elif disqualified:
            st.error("❌ Based on your answers, you do not meet one or more mandatory requirements for this role.")
        else:
            job_id = job_config["job_id"]
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_id = str(uuid.uuid4())[:8]

            # Save resume
            ext = os.path.splitext(uploaded_file.name)[1]
            resume_path = os.path.join(RESUMES_DIR, f"{name.replace(' ', '_')}_{job_id}_{file_id}{ext}")
            with open(resume_path, "wb") as out_file:
                out_file.write(uploaded_file.read())

            # Save answers to CSV
            csv_path = os.path.join(RESPONSES_DIR, f"responses_{job_id}.csv")
            row = pd.DataFrame([{
                "name": name,
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "answers": "|".join(map(str, answers)),
                "submitted_at": timestamp
            }])

            if os.path.exists(csv_path):
                existing = pd.read_csv(csv_path)
                full = pd.concat([existing, row], ignore_index=True)
            else:
                full = row

            full.to_csv(csv_path, index=False)
            st.success("🎉 Your application has been submitted successfully!")

else:
    st.info("Please enter a valid name, email, and phone number to continue.")
