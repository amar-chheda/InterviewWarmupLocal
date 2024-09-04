# Interview Warmup Local

Interview Warmup Local is a tool designed to help users practice and prepare for job interviews. It uses AI-powered speech recognition and language models to provide a realistic interview experience and feedback.

## Features

- Upload your resume and job description
- Add custom interview questions
- Practice answering questions with speech-to-text functionality
- Receive AI-generated feedback on your answers



## Demo

To see how Interview Warmup Local works, check out this demo video:

![Demo Video](assets/InterviewWarmupLocal.gif)

This video provides a step-by-step walkthrough of the application.


## High Level Architecture

![High Level Architecture](assets/Interview%20Warmup%20Local.png)

This diagram illustrates the overall structure and components of the Interview Warmup Local application.



## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the `config.yaml` file (see [Configuration](#configuration) section)
4. Run the Streamlit app:
   ```
   streamlit run main.py
   ```     

## Running the Streamlit App

To run the Interview Warmup Local app:

1. Open a terminal and navigate to the project directory
2. Run the following command:
   ```
   streamlit run main.py
   ```
3. The app should open in your default web browser

## Usage

1. Upload your resume and enter the job description
2. Add custom interview questions or use the provided ones
3. Start the practice session
4. Answer the questions by speaking (the app will transcribe your speech)
5. Review and edit your answers if needed
6. Get AI-generated feedback on your performance

## Customization

You can customize various aspects of the application by modifying the Python files:

- `main.py`: Main Streamlit application logic
- `interview_warmup_local/audio/speech_to_text.py`: Speech recognition functionality
- `interview_warmup_local/llm/local_llm.py`: Language model integration for analysis

## Configuration

The `config.yaml` file contains important settings for the application. Here are some key configurations you can modify:

### Voice Model

- `model_path`: Path to the voice model file
- `channels`: Number of audio channels (1 for mono, 2 for stereo)
- `sample_rate`: Sample rate for audio processing
- `chunk_size`: Size of audio chunks for processing
- `frames_per_buffer`: Number of frames per buffer for audio processing
- `model_type`: Type of model (e.g., "vosk", "whisper")

Example configuration:

```yaml
voice_model:
  model_path: "/path/to/model"
  channels: 1
  sample_rate: 16000
  chunk_size: 4096
```

### LLM (Language Model)

- `model`: Name or path of the language model to use (e.g., "eramax/fusechat-7b-varm")
- `request_timeout`: Timeout for LLM requests in seconds (e.g., 320.0)
- `chunk_size`: Size of text chunks for processing (e.g., 512)
- `chunk_overlap`: Overlap between text chunks (e.g., 75)
- `embed_model`: Name of the embedding model to use (e.g., "BAAI/bge-small-en-v1.5")
- `prompt_template`: Custom prompts for analysis
  - `overall_analysis`: Template for overall interview analysis
  - `question_analysis`: Template for individual question analysis

Example configuration:

```yaml
llm:
  model: "eramax/fusechat-7b-varm"
  request_timeout: 320.0
  chunk_size: 512
  chunk_overlap: 75
  embed_model: "BAAI/bge-small-en-v1.5"
  prompt_template:
    question_analysis: |
        You are an AI assistant tasked with evaluating a candidate's interview answer using a scoring matrix based on the job description and resume.

        Job Description:
        {job_description}

        Question:
        {question}

        Candidate’s Answer:
        {answer}

        Evaluate the candidate's answer based on its content, context, and relevance to the Question. 
        Consider whether the answer provides meaningful and useful information. If the answer does not provide enough useful information, state that clearly.

        Use the following criteria, with scores from 1 to 5 (1 = Poor, 5 = Excellent):
        1. Relevance of the answer to the question and job description.
        2. Clarity and coherence of the answer.
        3. Alignment with the job description requirements.
        5. Depth and usefulness of the information provided.

        Please provide your evaluation in this structured format:

        **Scoring Matrix**:
        - Relevance: [Score]
        - Clarity: [Score]
        - Alignment: [Score]
        - Use of Experience: [Score]
        - Depth of Information: [Score]

        **Detailed Feedback**:
        - Does the answer provide enough useful information? (Yes/No)
        - Key strengths (if applicable):
        - Areas for improvement:
        - Overall assessment of this answer:

    overall_analysis: |
      Based on the following individual question-answer analyses:
      {analyses}

      Resume:
      {resume}

      Job Description:
      {job_description}

      Provide an overall evaluation of the candidate's interview performance, ensuring that you consider the quality and depth of the answers, 
      not just the presence of keywords.

      Use the following criteria, with scores from 1 to 5 (1 = Poor, 5 = Excellent):
      1. Relevance and coherence across all answers.
      2. Alignment with the job description.
      3. Effective use of experience from the resume.
      4. Depth of information provided across answers.
      5. Consistency of performance across questions.

      Please provide your overall evaluation in this structured format:

      **Overall Scoring Matrix**:
      - Relevance & Coherence: [Score]
      - Alignment: [Score]
      - Use of Experience: [Score]
      - Depth of Information: [Score]
      - Consistency: [Score]    

      **Overall Summary**:
      - Were the answers generally meaningful and well thought out? (Yes/No)
      - Key strengths across the interview:
      - Areas for improvement across the interview:
      - Final assessment of candidate fit for the role:
```

## Contributing


We welcome contributions to improve Interview Warmup Local! Here's how you can contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

### Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

### Reporting Issues

If you find a bug or have a suggestion for improvement, please open an issue on the GitHub repository. When reporting issues, please provide as much detail as possible, including steps to reproduce the problem, expected behavior, and actual behavior.

Thank you for your contributions to make Interview Warmup Local better!

## License

This project is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
