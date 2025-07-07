import os
from typing import Optional

from ai_companion.core.exceptions import TextToSpeechError
from ai_companion.settings import settings
from elevenlabs import ElevenLabs, Voice, VoiceSettings

class TextToSpeech:
    """A class for converting text to speech using ElevenLabs API."""

    REQUIRED_ENV_VARS = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]

    def __init__(self):
        """Initialize the TextToSpeech class."""
        self._validate_env_vars()
        self._client: Optional[ElevenLabs] = None

    def _validate_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
    @property
    def client(self) -> ElevenLabs:
        """Get or create ElevenLabs client instance using singleton pattern."""
        if self._client is None:
            self._client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        return self._client
    
    async def synthesize(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech

        Returns:
            bytes: Audio data
        """
        if not text.strip():
            raise ValueError("Text cannot be empty or whitespace.")
        
        if len(text) > 5000: # eleven labs limit
            raise ValueError("Text exceeds the maximum length of 500 characters.")
        
        try:
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=settings.ELEVENLABS_VOICE_ID,
                voice_settings=VoiceSettings(
                  stability=0.5, similarity_boost=0.5  
                ),
                model_id=settings.TTS_MODEL_NAME
            )

            audio_bytes = b"".join(audio_generator)
            if not audio_bytes:
                raise TextToSpeechError("Failed to generate audio data.")
            
            return audio_bytes
        except Exception as e:
            raise TextToSpeechError(f"An error occurred while generating speech: {str(e)}") from e
