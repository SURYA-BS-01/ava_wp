# Ava - Conversational AI Companion

An intelligent conversational AI agent built with Chainlit for seamless human-AI interaction.

## What It Is

Ava is a conversational companion that talks to you like a friend. I gave it a character and personality, plus a weekly schedule to make interactions feel more natural and personal.

## Tech Stack

- **UI**: Chainlit
- **LLM**: Groq
- **Agent**: Langgraph
- **Voice**: ElevenLabs
- **Images**: TogetherAI
- **Vector DB**: Qdrant

## Features

- **Multi-modal responses** - Automatically chooses whether to respond with text, image, or audio based on context
- **Persona-driven** - Has a defined character that shapes how it interacts
- **Friend-like conversations** - Talks casually like a real companion
- **Weekly schedule** - Follows a schedule to make interactions feel more realistic
- **Text generation and understanding**
- **Image generation and understanding**  
- **Audio generation and understanding**

## How It Works

Ava automatically decides what type of response to give you:
- Text for normal conversations
- Images when visual content would be helpful
- Audio for more personal or expressive responses

The agent uses its persona to maintain consistent character throughout conversations.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
chainlit run app.py
```

Open `http://localhost:8000` and start chatting with Ava.

## Requirements

- Python 3.8+
- API keys for ElevenLabs, TogetherAI
- Qdrant instance
- Chainlit