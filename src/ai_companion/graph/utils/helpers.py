import re
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from ai_companion.settings import settings
from ai_companion.modules.image.text_to_image import TextToImage
from ai_companion.modules.speech.text_to_speech import TextToSpeech

def get_chat_model(temperature: float = 0.7):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
        model_name = settings.TEXT_MODEL_NAME,
    )

def remove_asterisk_content(text: str) -> str:
    """Remove content between asterisks from the text."""
    return re.sub(r"\*.*?\*", "", text).strip()

class AsteriskRemovalParser(StrOutputParser):
    def parse(self, text):
        return remove_asterisk_content(super().parse(text))
    
def get_text_to_image_module():
    return TextToImage()

def get_text_to_speech_module():
    return TextToSpeech()