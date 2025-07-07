# import asyncio
# from langchain_core.messages import HumanMessage
# from ai_companion.graph.state import AICompanionState
# from ai_companion.graph.nodes import image_node
# from langchain_core.runnables import RunnableConfig
# from dotenv import load_dotenv

# load_dotenv(".env")  # Load environment variables

# async def main():
#     # Create a test message
#     messages = [
#         HumanMessage(content="Can you show me a picture of a dog playing in the park?")
#     ]

#     # Set up initial state
#     state = AICompanionState(
#         messages=messages,
#         summary="",
#         workflow="image",
#         audio_buffer=b"",
#         image_path="",
#         current_activity="",   # This is important to test context detection
#         apply_activity=False,
#         memory_context=""
#     )

#     # Create a dummy config (empty dict is usually fine for testing)
#     config = RunnableConfig()

#     print("🚀 Running image_node with test message...")

#     # Run the image_node
#     result = await image_node(state, config)

#     # Print relevant parts of the result
#     print("\n✅ Image Node Result:")
#     print("👉 Image Path:", result.get("image_path"))
#     print("👉 Ava's Message:", result.get("messages").content)

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from langchain_core.messages import HumanMessage
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.nodes import audio_node
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv

load_dotenv(".env")  # Load environment variables

async def main():
    # Create a test message
    messages = [
        HumanMessage(content="Can you say hello in a friendly voice?")
    ]

    # Set up initial state
    state = AICompanionState(
        messages=messages,
        summary="",
        workflow="audio",
        audio_buffer=b"",
        image_path="",
        current_activity="",   # This is important to test context detection
        apply_activity=False,
        memory_context=""
    )

    # Create a dummy config (empty dict is usually fine for testing)
    config = RunnableConfig()

    print("🚀 Running audio_node with test message...")

    # Run the audio_node
    result = await audio_node(state, config)

    # Print relevant parts of the result
    print("\n✅ Audio Node Result:")
    print("👉 Audio Buffer Length:", len(result.get("audio_buffer", b"")))
    print("👉 Ava's Message:", getattr(result.get("messages"), "content", result.get("messages")))

    # Optionally, save the audio to a file for manual verification
    if result.get("audio_buffer"):
        with open("test_output_audio.wav", "wb") as f:
            f.write(result["audio_buffer"])
        print("👉 Audio saved to test_output_audio.wav")

if __name__ == "__main__":
    asyncio.run(main())