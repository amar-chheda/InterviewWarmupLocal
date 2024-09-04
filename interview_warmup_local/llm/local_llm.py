# standard imports
import os
from llama_index.core import ServiceContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Settings
from loguru import logger
import PyPDF2
from llama_index.core.prompts import PromptTemplate

# custom imports
from interview_warmup_local.utils import LLMConfig

# typing imports
from typing import List, Dict


class InterviewAnalyzer:
    def __init__(self, llm_config: LLMConfig):
        self.llm = None
        self.index = None
        self.llm_config = llm_config
        self.prompt_templates = {
            'analyze_answer': PromptTemplate(llm_config.prompt_template['question_analysis']),
            'overall_analysis': PromptTemplate(llm_config.prompt_template['overall_analysis'])
        }

    def initialize_llm(self):
        """
        Initialize the LLM using Ollama with the configured model.
        """
        self.llm = Ollama(model=self.llm_config.model, request_timeout=self.llm_config.request_timeout)
        Settings.llm = self.llm
        Settings.chunk_size = self.llm_config.chunk_size
        Settings.chunk_overlap = self.llm_config.chunk_overlap
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=self.llm_config.embed_model
        )
        logger.info("LLM initialized")
        return self.llm

    def create_index(self, resume_path: str, job_description_path: str):
        """
        Create an index from the resume and job description using local embeddings.
        """
        logger.debug(f"Creating index from resume: {resume_path} and job description: {job_description_path}")

        documents = SimpleDirectoryReader(input_files=[resume_path, job_description_path]).load_data()
        self.initialize_llm()

        node_parser = SimpleNodeParser.from_defaults()
        nodes = node_parser.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(nodes)
        logger.info("Index created")
        return self.index

    def analyze_answer(self, question: str, answer: str, job_description: str, resume: str) -> str:
        """
        Analyze a single question-answer pair.
        """
        logger.debug(f"Analyzing answer for question: {question}")
        prompt = self.prompt_templates['analyze_answer'].format(
            question=question,
            answer=answer,
            job_description=job_description
        )

        query_engine = self.index.as_query_engine()
        response = query_engine.query(prompt)
        logger.debug(f"Analysis response: {response}")
        return str(response)

    def process_interview_data(self, resume_path: str, job_description_path: str, questions: List[str], answers: List[str]) -> List[str]:
        """
        Process the interview data and generate an analysis for each question-answer pair.
        """
        logger.info("Starting interview data processing")
        # Read job description content
        with open(job_description_path, 'r') as file:
            self.job_description = file.read()
        logger.debug("Job description loaded")

        # Read resume content (PDF)
        with open(resume_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            self.resume = ""
            for page in pdf_reader.pages:
                self.resume += page.extract_text()
        logger.debug("Resume loaded")

        # Create index using settings
        _ = self.create_index(resume_path, job_description_path)

        analyses = []
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            logger.debug(f"Processing question {i} of {len(questions)}")
            analysis = self.analyze_answer(question, answer, self.job_description, self.resume)
            analyses.append(analysis)

        logger.info("Interview data processing completed")
        return analyses

    def generate_overall_analysis(self, analyses: List[str]) -> str:
        """
        Generate an overall analysis based on individual question-answer analyses.
        """
        logger.info("Generating overall analysis")
        prompt = self.prompt_templates['overall_analysis'].format(
            analyses=' '.join(analyses),
            resume=self.resume,
            job_description=self.job_description
        )
        response = self.llm.complete(prompt)
        logger.debug(f"Overall analysis response: {response}")

        logger.info("Overall analysis generation completed")
        return str(response)

    def set_prompt_template(self, template_name: str, new_template: str):
        """
        Set a new prompt template for a specific analysis type.
        """
        if template_name in self.prompt_templates:
            self.prompt_templates[template_name] = PromptTemplate(new_template)
            logger.info(f"Updated prompt template for {template_name}")
        else:
            logger.error(f"Template name {template_name} not found")

    def get_prompt_template(self, template_name: str) -> str:
        """
        Get the current prompt template for a specific analysis type.
        """
        template = self.prompt_templates.get(template_name)
        return template.template if template else "Template not found"
