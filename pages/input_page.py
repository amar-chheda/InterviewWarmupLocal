import streamlit as st
from pathlib import Path
import json
import random

def input_page():
    st.header("Prepare for Your Interview")

    data_path = Path("./data")
    
    # Load questions
    questions_file = data_path / "questions.json"
    if questions_file.exists() and not st.session_state.questions:
        with open(questions_file, "r") as f:
            st.session_state.questions = json.load(f)

    # Load job description
    job_description_file = data_path / "job_description.txt"
    if job_description_file.exists() and not st.session_state.job_description:
        with open(job_description_file, "r") as f:
            st.session_state.job_description = f.read()

    # Check for resume
    resume_files = list(data_path.glob("*.pdf")) + list(data_path.glob("*.docx"))
    if resume_files and not st.session_state.resume:
        st.session_state.resume = resume_files[0]

    # Input for questions
    st.subheader("Interview Questions")
    new_question = st.text_input("Add a new question:")
    if st.button("Add Question"):
        if new_question:
            st.session_state.questions.append(new_question)
            st.success("New question added successfully!")
        else:
            st.warning("Please enter a question before adding.")
    st.write(st.session_state.questions)

    # Job description input
    st.subheader("Job Description")
    st.session_state.job_description = st.text_area("Enter the job description:", value=st.session_state.job_description)
    if st.button("Submit Job Description"):
        st.success("Job description submitted successfully!")

    # Resume upload
    st.subheader("Upload Your Resume")
    if st.session_state.resume and isinstance(st.session_state.resume, Path):
        st.write(f"Current resume: {st.session_state.resume.name}")
        if st.button("Remove current resume"):
            st.session_state.resume = None
    else:
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
        if uploaded_file:
            st.session_state.resume = uploaded_file

    if st.button("Start Practice"):
        if st.session_state.questions and st.session_state.job_description and st.session_state.resume:
            save_data(data_path, questions_file, job_description_file)
            st.session_state.page = 'practice'
            st.session_state.practice_questions = random.sample(st.session_state.questions, 1)
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.success("Data saved successfully. Starting practice...")
            st.rerun()
        else:
            if not st.session_state.job_description:
                st.error("Please enter the job description before starting.")
            if not st.session_state.resume:
                st.error("Please upload your resume before starting.")

def save_data(data_path, questions_file, job_description_file):
    data_path.mkdir(parents=True, exist_ok=True)
    with open(questions_file, "w") as f:
        json.dump(st.session_state.questions, f)
    with open(job_description_file, "w") as f:
        f.write(st.session_state.job_description)
    if not isinstance(st.session_state.resume, Path):
        resume_path = data_path / st.session_state.resume.name
        with open(resume_path, "wb") as f:
            f.write(st.session_state.resume.getbuffer())
