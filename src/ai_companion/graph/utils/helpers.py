from langchain_groq import ChatGroq
from ai_companion.settings import settings

def get_chat_model(temperature: float = 0.7):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
        model_name = settings.TEXT_MODEL_NAME,
    )