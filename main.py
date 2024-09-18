import streamlit as st
from pathlib import Path
import random

from interview_warmup_local.utils import read_config, download_ollama_model
from interview_warmup_local.audio.speech_to_text import initialize_speech_to_text
from interview_warmup_local.utils import ConfigModel

from pages.input_page import input_page
from pages.practice_page import practice_page
from pages.evaluation_page import evaluation_page

def initialize_app(config: ConfigModel):
    stt_model = initialize_speech_to_text(config.voice_model)
    return stt_model

def main(config: ConfigModel):
    stt_model = initialize_app(config)
    st.set_page_config(page_title="Interview Warmup Local", layout="wide")
    st.title("Interview Warmup Local")

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
        evaluation_page(config)

if __name__ == "__main__":
    config = read_config("./config.yaml")  
    download_ollama_model(config.llm.embed_model)
    download_ollama_model(config.llm.model)
    main(config=config)
