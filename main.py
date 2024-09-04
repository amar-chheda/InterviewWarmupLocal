# standard imports
import streamlit as st
import random
from pathlib import Path
import json

# custom imports
from interview_warmup_local.utils import read_config
from interview_warmup_local.audio.speech_to_text import initialize_speech_to_text
from interview_warmup_local.llm.local_llm import InterviewAnalyzer

# typing imports
from typing import List, Dict
from interview_warmup_local.utils import ConfigModel

def initialize_app(config: ConfigModel):
    # Initialize speech-to-text model
    stt_model = initialize_speech_to_text(config.voice_model)
    return stt_model

def main(config: ConfigModel):
    stt_model = initialize_app(config)
    st.set_page_config(page_title="Interview Warmup Local", layout="wide")
    st.title("Interview Warmup Local")

    # Check if session state is initialized
    if 'page' not in st.session_state:
        st.session_state.page = 'input'
        st.session_state.questions = []
        st.session_state.job_description = ""
        st.session_state.resume = None

    if st.session_state.page == 'input':
        input_page()
    elif st.session_state.page == 'practice':
        practice_page(stt_model)
    elif st.session_state.page == 'evaluation':
        evaluation_page()

def input_page():
    st.header("Prepare for Your Interview")

    # Pre-load data from files if they exist
    data_path = Path("./data")
    
    # Load questions if file exists and the list of questions is empty
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

    # Add new question
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
            # Save questions as JSON
            data_path.mkdir(parents=True, exist_ok=True)
            with open(questions_file, "w") as f:
                json.dump(st.session_state.questions, f)

            # Save job description as txt
            with open(job_description_file, "w") as f:
                f.write(st.session_state.job_description)

            # Save resume
            if isinstance(st.session_state.resume, Path):
                resume_path = st.session_state.resume
            else:
                resume_path = data_path / st.session_state.resume.name
                with open(resume_path, "wb") as f:
                    f.write(st.session_state.resume.getbuffer())

            st.session_state.page = 'practice'
            st.session_state.practice_questions = random.sample(st.session_state.questions, 1) # this needs to go as config setting
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.success("Data saved successfully. Starting practice...")
            st.rerun()  # Force a rerun to switch to practice page
        else:
            if not st.session_state.job_description:
                st.error("Please enter the job description before starting.")
            if not st.session_state.resume:
                st.error("Please upload your resume before starting.")

def practice_page(stt_model):
    st.header("Practice Interview")
    
    for i, question in enumerate(st.session_state.practice_questions):
        st.subheader(f"Question {i+1}:")
        st.write(question)
        
        # Initialize answer in session state if not present
        if f"answer_{i}" not in st.session_state:
            st.session_state[f"answer_{i}"] = ""

        if st.button("🎙️ Record", key=f"record_btn_{i}"):
            st.write("Say 'stop now' to end recording")
            
            # Call the speech_to_text function with the initialized model
            answer = stt_model.transcribe_audio()
            
            # Store the answer
            st.session_state[f"answer_{i}"] = answer
            st.session_state.answers = [st.session_state.get(f"answer_{j}", "") for j in range(len(st.session_state.practice_questions))]

        # Display and allow editing of the answer
        if st.session_state[f"answer_{i}"]:
            st.subheader("Your Answer:")
            edited_answer = st.text_area("Edit your answer if needed:", 
                                         value=st.session_state[f"answer_{i}"], 
                                         key=f"edit_answer_{i}")
            if st.button("✏️ Update Answer", key=f"update_btn_{i}"):
                st.session_state[f"answer_{i}"] = edited_answer
                st.session_state.answers = [st.session_state.get(f"answer_{j}", "") for j in range(len(st.session_state.practice_questions))]
                st.success("Answer updated successfully!")
        
        # Always display the current answer for this question
        st.subheader("Your Current Answer:")
        st.write(st.session_state.get(f"answer_{i}", "No answer provided yet."))
        
        st.markdown("---")  # Add a separator between questions
    
    # If all questions have been answered, show a button to proceed to evaluation
    if all(st.session_state.get(f"answer_{i}", "") for i in range(len(st.session_state.practice_questions))):
        if st.button("Finish Practice and See Evaluation"):
            st.session_state.page = 'evaluation'
            st.rerun()
    
    

def evaluation_page():
    st.header("Interview Evaluation")
    st.write("Thank you for completing the practice interview!")
    st.write("Your answers are being evaluated...")

    # Initialize InterviewAnalyzer
    analyzer = InterviewAnalyzer(config.llm)

    resume_path = "./data/" + st.session_state.resume.name
    job_description_path = "./data/job_description.txt"
    
    with st.spinner("Analyzing your responses..."):
        analyses = analyzer.process_interview_data(
            resume_path, 
            job_description_path, 
            st.session_state.practice_questions, 
            st.session_state.answers
        )

    # Display individual question-answer evaluations
    for q, a, analysis in zip(st.session_state.practice_questions, st.session_state.answers, analyses):
        with st.expander(f"Question: {q}"):
            st.subheader("Your Answer:")
            st.write(a)
            st.subheader("Evaluation:")
            st.write(analysis)

    # Generate and display overall analysis
    with st.spinner("Generating overall analysis..."):
        overall_analysis = analyzer.generate_overall_analysis(analyses)
    
    st.subheader("Overall Analysis:")
    st.write(overall_analysis)

    if st.button("Start New Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    config = read_config("./config.yaml")  
    main(config=config)
