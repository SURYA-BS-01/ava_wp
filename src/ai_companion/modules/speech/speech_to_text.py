import os
import tempfile
from typing import Optional

from io import BytesIO
import wave
import audioop
from pydub import AudioSegment

from ai_companion.core.exceptions import SpeechToTextError
from ai_companion.settings import settings
from groq import Groq

class SpeechToText:
    """A class to handle speech-to-text conversion using Groq's Whisper model."""

    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]

    def __init__(self):
        """Initialize the SpeechToText class and validate environment variables."""
        self._validate_env_vars()
        self._client: Optional[Groq] = None

    def _validate_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @property
    def client(self) -> Groq:
        """Get or create Groq client instance using singleton pattern."""
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Convert speech to text using Groq's Whisper model.

        Args:
            audio_data: Binary audio data

        Returns:
            str: Transcribed text
        """

        if not audio_data:
            raise ValueError("Audio data cannot be empty")

        try:
            # Convert audio data to WAV format using pydub
            try:
                # Try to detect and convert the audio format
                audio_segment = AudioSegment.from_file(BytesIO(audio_data))
                
                # Convert to WAV format with standard settings
                wav_buffer = BytesIO()
                audio_segment.export(
                    wav_buffer,
                    format="wav",
                    parameters=["-ac", "1", "-ar", "16000"]  # Mono, 16kHz
                )
                wav_data = wav_buffer.getvalue()
                
            except Exception as e:
                print(f"Pydub conversion failed: {e}")
                # Fallback: assume it's raw PCM and create WAV header
                wav_data = self._create_wav_from_pcm(audio_data)

            # Create a temporary file with .wav extension
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_file_path = temp_file.name

            try:
                # Verify the file is valid before sending
                if not self._is_valid_wav_file(temp_file_path):
                    raise ValueError("Generated WAV file is not valid")

                # Open the temporary file for the API request
                with open(temp_file_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3-turbo",
                        language="en",
                        response_format="text",
                    )

                if not transcription:
                    raise SpeechToTextError("Transcription result is empty")

                return transcription

            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            raise SpeechToTextError(f"Speech-to-text conversion failed: {str(e)}") from e

    def _create_wav_from_pcm(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """Create a WAV file from raw PCM data."""
        wav_buffer = BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        return wav_buffer.getvalue()

    def _is_valid_wav_file(self, file_path: str) -> bool:
        """Check if the file is a valid WAV file."""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # Try to read basic properties
                wav_file.getnchannels()
                wav_file.getsampwidth()
                wav_file.getframerate()
                wav_file.getnframes()
                return True
        except Exception:
            return False