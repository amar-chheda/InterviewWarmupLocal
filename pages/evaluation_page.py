import streamlit as st
from interview_warmup_local.llm.local_llm import InterviewAnalyzer

def evaluation_page(config):
    st.header("Interview Evaluation")
    st.write("Thank you for completing the practice interview!")
    st.write("Your answers are being evaluated...")

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

    for q, a, analysis in zip(st.session_state.practice_questions, st.session_state.answers, analyses):
        with st.expander(f"Question: {q}"):
            st.subheader("Your Answer:")
            st.write(a)
            st.subheader("Evaluation:")
            st.write(analysis)

    with st.spinner("Generating overall analysis..."):
        overall_analysis = analyzer.generate_overall_analysis(analyses)
    
    st.subheader("Overall Analysis:")
    st.write(overall_analysis)

    if st.button("Start New Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
