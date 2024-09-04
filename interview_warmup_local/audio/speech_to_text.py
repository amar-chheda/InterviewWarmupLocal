# standard imports
import pyaudio
import json
import whisper
import numpy as np
from loguru import logger
import re

#custom imports


# typing imports
from interview_warmup_local.utils import VoiceModelConfig
from typing import List


class SpeechToText:
    def __init__(self, voice_model_config: VoiceModelConfig):
        self.config = voice_model_config
        self.model = None
        self.recognizer = None
        self.load_model()

    def load_model(self):
        """Load the speech recognition model based on the configuration."""
        try:
            if self.config.model_type.lower() == "vosk":
                from vosk import Model, KaldiRecognizer
                self.model = Model(self.config.model_path)
                self.recognizer = KaldiRecognizer(self.model, self.config.sample_rate)
            elif self.config.model_type.lower() == "whisper":
                self.model = whisper.load_model("tiny.en")
            else:
                raise ValueError(f"Unsupported model type: {self.config.model_type}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def transcribe_audio(self) -> str:
        """
        Record audio and transcribe it to text when called.
        
        Returns:
            str: The recognized text.
        """
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paFloat32, 
                            channels=self.config.channels, 
                            rate=self.config.sample_rate, 
                            input=True, 
                            frames_per_buffer=self.config.frames_per_buffer)

            recognized_text = ""
            audio_data: List[np.ndarray] = []
            
            logger.info("Listening... Say 'stop now' to stop.")
            while True:
                try:
                    data = stream.read(self.config.chunk_size, exception_on_overflow=False)
                    if self.config.model_type.lower() == "vosk":
                        recognized_text += self._process_vosk(data)
                    else:  # Whisper
                        recognized_text += self._process_whisper(data, audio_data)
                    
                    logger.info(recognized_text)
                    
                    # Check for the termination keyword
                    if "stop now" in recognized_text.lower():
                        logger.info("Termination keyword detected. Stopping...")
                        break
                    
                except OSError as e:
                    if e.errno == -9981:  # Input overflowed
                        logger.warning("Warning: Input overflowed. Continuing...")
                        continue
                    else:
                        logger.error(f"Error during audio processing: {str(e)}")
                        raise  # Re-raise the exception if it's not an input overflow

            stream.stop_stream()
            stream.close()
            p.terminate()

            return re.sub(r'(?i)stop now', '', recognized_text).strip()
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}")
            raise

    def _process_vosk(self, data: bytes) -> str:
        """Process audio data using Vosk model."""
        try:
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                return result['text'] + " "
            return ""
        except Exception as e:
            logger.error(f"Error in _process_vosk: {str(e)}")
            return ""

    def _process_whisper(self, data: bytes, audio_data: List[np.ndarray]) -> str:
        """Process audio data using Whisper model."""
        try:
            audio_data.append(np.frombuffer(data, dtype=np.float32))
            if len(audio_data) > 50:  # Process ~3 seconds of audio at a time
                audio_chunk = np.concatenate(audio_data)
                result = self.model.transcribe(audio_chunk)
                audio_data.clear()  # Clear processed audio data
                return result['text'] + " "
            return ""
        except Exception as e:
            logger.error(f"Error in _process_whisper: {str(e)}")
            return ""

def initialize_speech_to_text(voice_model_config: VoiceModelConfig) -> SpeechToText:
    """
    Initialize the SpeechToText model.
    
    Args:
        voice_model_config (VoiceModelConfig): Configuration for the voice model.
    
    Returns:
        SpeechToText: Initialized SpeechToText object.
    """
    try:
        return SpeechToText(voice_model_config)
    except Exception as e:
        logger.error(f"Error initializing SpeechToText: {str(e)}")
        raise