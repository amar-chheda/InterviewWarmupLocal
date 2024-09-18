import streamlit as st

def practice_page(stt_model):
    st.header("Practice Interview")
    
    for i, question in enumerate(st.session_state.practice_questions):
        st.subheader(f"Question {i+1}:")
        st.write(question)
        
        if f"answer_{i}" not in st.session_state:
            st.session_state[f"answer_{i}"] = ""

        if st.button("🎙️ Record", key=f"record_btn_{i}"):
            st.write("Say 'stop now' to end recording")
            answer = stt_model.transcribe_audio()
            st.session_state[f"answer_{i}"] = answer
            update_answers()

        if st.session_state[f"answer_{i}"]:
            st.subheader("Your Answer:")
            edited_answer = st.text_area("Edit your answer if needed:", 
                                         value=st.session_state[f"answer_{i}"], 
                                         key=f"edit_answer_{i}")
            if st.button("✏️ Update Answer", key=f"update_btn_{i}"):
                st.session_state[f"answer_{i}"] = edited_answer
                update_answers()
                st.success("Answer updated successfully!")
        
        st.subheader("Your Current Answer:")
        st.write(st.session_state.get(f"answer_{i}", "No answer provided yet."))
        
        st.markdown("---")
    
    if all(st.session_state.get(f"answer_{i}", "") for i in range(len(st.session_state.practice_questions))):
        if st.button("Finish Practice and See Evaluation"):
            st.session_state.page = 'evaluation'
            st.rerun()

def update_answers():
    st.session_state.answers = [st.session_state.get(f"answer_{j}", "") for j in range(len(st.session_state.practice_questions))]
