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


class LocalLLMHandler:
    def __init__(self, llm_config: LLMConfig):
        self.llm = None
        self.index = None
        self.llm_config = llm_config

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

    def create_index(self, input_files: List[str]):
        """
        Create an index from the given input files using local embeddings.
        """
        logger.debug(f"Creating index from files: {input_files}")

        documents = SimpleDirectoryReader(input_files=input_files).load_data()
        self.initialize_llm()

        node_parser = SimpleNodeParser.from_defaults()
        nodes = node_parser.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(nodes)
        logger.info("Index created")
        return self.index

    def query_index(self, prompt: str) -> str:
        """
        Query the index with a given prompt.
        """
        if not self.index:
            raise ValueError("Index has not been created. Call create_index() first.")

        query_engine = self.index.as_query_engine()
        response = query_engine.query(prompt)
        return str(response)

    def complete_prompt(self, prompt: str) -> str:
        """
        Complete a prompt using the LLM.
        """
        if not self.llm:
            raise ValueError("LLM has not been initialized. Call initialize_llm() first.")

        response = self.llm.complete(prompt)
        return str(response)


class InterviewAnalyzer:
    def __init__(self, llm_config: LLMConfig):
        self.llm_handler = LocalLLMHandler(llm_config)
        self.prompt_templates = {
            'analyze_answer': PromptTemplate(llm_config.prompt_template['question_analysis']),
            'overall_analysis': PromptTemplate(llm_config.prompt_template['overall_analysis'])
        }
        self.job_description = ""
        self.resume = ""

    def analyze_answer(self, question: str, answer: str) -> str:
        """
        Analyze a single question-answer pair.
        """
        logger.debug(f"Analyzing answer for question: {question}")
        prompt = self.prompt_templates['analyze_answer'].format(
            question=question,
            answer=answer,
            job_description=self.job_description
        )

        response = self.llm_handler.query_index(prompt)
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
        _ = self.llm_handler.create_index([resume_path, job_description_path])

        analyses = []
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            logger.debug(f"Processing question {i} of {len(questions)}")
            analysis = self.analyze_answer(question, answer)
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
        response = self.llm_handler.complete_prompt(prompt)
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
