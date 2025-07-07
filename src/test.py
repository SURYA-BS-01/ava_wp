import asyncio
from langchain_core.messages import HumanMessage
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.nodes import image_node
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv

load_dotenv(".env")  # Load environment variables

async def main():
    # Create a test message
    messages = [
        HumanMessage(content="Can you show me a picture of a dog playing in the park?")
    ]

    # Set up initial state
    state = AICompanionState(
        messages=messages,
        summary="",
        workflow="image",
        audio_buffer=b"",
        image_path="",
        current_activity="",   # This is important to test context detection
        apply_activity=False,
        memory_context=""
    )

    # Create a dummy config (empty dict is usually fine for testing)
    config = RunnableConfig()

    print("🚀 Running image_node with test message...")

    # Run the image_node
    result = await image_node(state, config)

    # Print relevant parts of the result
    print("\n✅ Image Node Result:")
    print("👉 Image Path:", result.get("image_path"))
    print("👉 Ava's Message:", result.get("messages").content)

if __name__ == "__main__":
    asyncio.run(main())