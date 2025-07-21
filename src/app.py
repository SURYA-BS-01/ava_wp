# from dotenv import load_dotenv
# import os
# load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# from io import BytesIO

# import chainlit as cl
# from langchain_core.messages import AIMessageChunk, HumanMessage
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# from ai_companion.graph.graph import graph_builder
# from ai_companion.modules.image.image_to_text import ImageToText
# from ai_companion.modules.speech.speech_to_text import SpeechToText
# from ai_companion.modules.speech.text_to_speech import TextToSpeech
# from ai_companion.settings import settings

# # Global module instances
# speech_to_text = SpeechToText()
# text_to_speech = TextToSpeech()
# image_to_text = ImageToText()


# @cl.on_chat_start
# async def on_chat_start():
#     """Initialize the chat session"""
#     # thread_id = cl.user_session.get("id")
#     cl.user_session.set("thread_id", 1)


# @cl.on_message
# async def on_message(message: cl.Message):
#     """Handle text messages and images"""
#     msg = cl.Message(content="")

#     # Process any attached images
#     content = message.content
#     if message.elements:
#         for elem in message.elements:
#             if isinstance(elem, cl.Image):
#                 # Read image file content
#                 with open(elem.path, "rb") as f:
#                     image_bytes = f.read()

#                 # Analyze image and add to message content
#                 try:
#                     # Use global ImageToText instance
#                     description = await image_to_text.analyze_image(
#                         image_bytes,
#                         "Please describe what you see in this image in the context of our conversation.",
#                     )
#                     # content += f"\n[Image Analysis: {description}]"
#                     msg.content = description
#                 except Exception as e:
#                     cl.logger.warning(f"Failed to analyze image: {e}")

#     # Process through graph with enriched message content
#     thread_id = cl.user_session.get("thread_id")

#     async with cl.Step(type="run"):
#         async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
#             graph = graph_builder.compile(checkpointer=short_term_memory)
#             async for chunk in graph.astream(
#                 {"messages": [HumanMessage(content=content)]},
#                 {"configurable": {"thread_id": thread_id}},
#                 stream_mode="messages",
#             ):
#                 if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
#                     await msg.stream_token(chunk[0].content)

#             output_state = await graph.aget_state(config={"configurable": {"thread_id": thread_id}})

#     if output_state.values.get("workflow") == "audio":
#         response = output_state.values["messages"][-1].content
#         audio_buffer = output_state.values["audio_buffer"]
#         output_audio_el = cl.Audio(
#             name="Audio",
#             auto_play=True,
#             mime="audio/mpeg3",
#             content=audio_buffer,
#         )
#         await cl.Message(content=response, elements=[output_audio_el]).send()
#     elif output_state.values.get("workflow") == "image":
#         response = output_state.values["messages"][-1].content
#         image = cl.Image(path=output_state.values["image_path"], display="inline")
#         await cl.Message(content=response, elements=[image]).send()
#     else:
#         await msg.send()


# @cl.on_audio_chunk
# async def on_audio_chunk(chunk):
#     """Handle incoming audio chunks"""
#     if chunk.isStart:
#         buffer = BytesIO()
#         buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
#         cl.user_session.set("audio_buffer", buffer)
#         cl.user_session.set("audio_mime_type", chunk.mimeType)
#     cl.user_session.get("audio_buffer").write(chunk.data)


# @cl.on_audio_end
# async def on_audio_end(elements):
#     """Process completed audio input"""
#     # Get audio data
#     audio_buffer = cl.user_session.get("audio_buffer")
#     audio_buffer.seek(0)
#     audio_data = audio_buffer.read()

#     # Show user's audio message
#     input_audio_el = cl.Audio(mime="audio/mpeg3", content=audio_data)
#     await cl.Message(author="You", content="", elements=[input_audio_el, *elements]).send()

#     # Use global SpeechToText instance
#     transcription = await speech_to_text.transcribe(audio_data)

#     thread_id = cl.user_session.get("thread_id")

#     async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
#         graph = graph_builder.compile(checkpointer=short_term_memory)
#         output_state = await graph.ainvoke(
#             {"messages": [HumanMessage(content=transcription)]},
#             {"configurable": {"thread_id": thread_id}},
#         )

#     # Use global TextToSpeech instance
#     audio_buffer = await text_to_speech.synthesize(output_state["messages"][-1].content)

#     output_audio_el = cl.Audio(
#         name="Audio",
#         auto_play=True,
#         mime="audio/mpeg3",
#         content=audio_buffer,
#     )
#     await cl.Message(content=output_state["messages"][-1].content, elements=[output_audio_el]).send()


from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from io import BytesIO

import chainlit as cl
from chainlit.types import InputAudioChunk, OutputAudioChunk
from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ai_companion.graph.graph import graph_builder
from ai_companion.modules.image.image_to_text import ImageToText
from ai_companion.modules.speech.speech_to_text import SpeechToText
from ai_companion.modules.speech.text_to_speech import TextToSpeech
from ai_companion.settings import settings

# Global module instances
speech_to_text = SpeechToText()
text_to_speech = TextToSpeech()
image_to_text = ImageToText()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session"""
    # thread_id = cl.user_session.get("id")
    cl.user_session.set("thread_id", 1)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle text messages and images"""
    msg = cl.Message(content="")

    # Process any attached images
    content = message.content
    if message.elements:
        for elem in message.elements:
            if isinstance(elem, cl.Image):
                # Read image file content
                with open(elem.path, "rb") as f:
                    image_bytes = f.read()

                # Analyze image and add to message content
                try:
                    # Use global ImageToText instance
                    description = await image_to_text.analyze_image(
                        image_bytes,
                        "Please describe what you see in this image in the context of our conversation.",
                    )
                    # content += f"\n[Image Analysis: {description}]"
                    msg.content = description
                except Exception as e:
                    cl.logger.warning(f"Failed to analyze image: {e}")

    # Process through graph with enriched message content
    thread_id = cl.user_session.get("thread_id")

    async with cl.Step(type="run"):
        async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
            graph = graph_builder.compile(checkpointer=short_term_memory)
            async for chunk in graph.astream(
                {"messages": [HumanMessage(content=content)]},
                {"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            ):
                if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
                    await msg.stream_token(chunk[0].content)

            output_state = await graph.aget_state(config={"configurable": {"thread_id": thread_id}})

    if output_state.values.get("workflow") == "audio":
        response = output_state.values["messages"][-1].content
        audio_buffer = output_state.values["audio_buffer"]
        output_audio_el = cl.Audio(
            name="Audio",
            auto_play=True,
            mime="audio/mpeg3",
            content=audio_buffer,
        )
        await cl.Message(content=response, elements=[output_audio_el]).send()
    elif output_state.values.get("workflow") == "image":
        response = output_state.values["messages"][-1].content
        image = cl.Image(path=output_state.values["image_path"], display="inline")
        await cl.Message(content=response, elements=[image]).send()
    else:
        await msg.send()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session"""
    # thread_id = cl.user_session.get("id")
    cl.user_session.set("thread_id", 1)

@cl.on_audio_start
async def on_audio_start():
    """Initialize audio session"""
    # Initialize audio buffer for the session
    buffer = BytesIO()
    cl.user_session.set("audio_buffer", buffer)
    return True  # Enable audio connection


@cl.on_audio_chunk
async def on_audio_chunk(chunk: InputAudioChunk):
    """Handle incoming audio chunks"""
    # Get or create audio buffer
    audio_buffer = cl.user_session.get("audio_buffer")
    if audio_buffer is None:
        audio_buffer = BytesIO()
        cl.user_session.set("audio_buffer", audio_buffer)
    
    # Write chunk data to buffer
    audio_buffer.write(chunk.data)
    
    # Store mime type for later use
    cl.user_session.set("audio_mime_type", chunk.mimeType)


@cl.on_audio_end
async def on_audio_end():
    """Process completed audio input"""
    # Get audio data
    audio_buffer = cl.user_session.get("audio_buffer")
    if audio_buffer is None:
        cl.logger.warning("No audio buffer found")
        return
    
    audio_buffer.seek(0)
    audio_data = audio_buffer.read()
    
    # Check if we have valid audio data
    if not audio_data or len(audio_data) < 1000:  # Minimum reasonable audio size
        cl.logger.warning("Audio data is too small or empty")
        await cl.Message(content="Sorry, I didn't receive enough audio data. Please try speaking for a bit longer.").send()
        # Clean up and return
        cl.user_session.set("audio_buffer", None)
        return

    # Show user's audio message
    input_audio_el = cl.Audio(mime="audio/mpeg3", content=audio_data)
    await cl.Message(author="You", content="", elements=[input_audio_el]).send()

    try:
        # Use global SpeechToText instance
        transcription = await speech_to_text.transcribe(audio_data)
        
        if not transcription or transcription.strip() == "":
            await cl.Message(content="Sorry, I couldn't understand the audio. Please try again.").send()
            return

        cl.logger.info(f"Transcribed: {transcription}")

        thread_id = cl.user_session.get("thread_id")

        async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
            graph = graph_builder.compile(checkpointer=short_term_memory)
            output_state = await graph.ainvoke(
                {"messages": [HumanMessage(content=transcription)]},
                {"configurable": {"thread_id": thread_id}},
            )

        # Use global TextToSpeech instance
        response_text = output_state["messages"][-1].content
        audio_buffer = await text_to_speech.synthesize(response_text)

        # For streaming audio back to client, you can use:
        # await cl.context.emitter.send_audio_chunk(
        #     OutputAudioChunk(
        #         mimeType="pcm16",
        #         data=audio_buffer,
        #         track="response_audio"
        #     )
        # )

        # Or use the traditional approach with Audio element
        output_audio_el = cl.Audio(
            name="Audio",
            auto_play=True,
            mime="audio/mpeg3",
            content=audio_buffer,
        )
        await cl.Message(content=response_text, elements=[output_audio_el]).send()
        
    except Exception as e:
        cl.logger.error(f"Error processing audio: {e}")
        await cl.Message(content="Sorry, I encountered an error processing your audio. Please try again.").send()
    
    finally:
        # Clean up audio buffer
        cl.user_session.set("audio_buffer", None)

# @cl.on_audio_chunk
# async def on_audio_chunk(chunk):
#     """Handle incoming audio chunks"""
#     if chunk.isStart:
#         buffer = BytesIO()
#         buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
#         cl.user_session.set("audio_buffer", buffer)
#         cl.user_session.set("audio_mime_type", chunk.mimeType)
#     cl.user_session.get("audio_buffer").write(chunk.data)


# @cl.on_audio_end
# async def on_audio_end(elements):
#     """Process completed audio input"""
#     # Get audio data
#     audio_buffer = cl.user_session.get("audio_buffer")
#     audio_buffer.seek(0)
#     audio_data = audio_buffer.read()

#     # Show user's audio message
#     input_audio_el = cl.Audio(mime="audio/mpeg3", content=audio_data)
#     await cl.Message(author="You", content="", elements=[input_audio_el, *elements]).send()

#     # Use global SpeechToText instance
#     transcription = await speech_to_text.transcribe(audio_data)

#     thread_id = cl.user_session.get("thread_id")

#     async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
#         graph = graph_builder.compile(checkpointer=short_term_memory)
#         output_state = await graph.ainvoke(
#             {"messages": [HumanMessage(content=transcription)]},
#             {"configurable": {"thread_id": thread_id}},
#         )

#     # Use global TextToSpeech instance
#     audio_buffer = await text_to_speech.synthesize(output_state["messages"][-1].content)

#     output_audio_el = cl.Audio(
#         name="Audio",
#         auto_play=True,
#         mime="audio/mpeg3",
#         content=audio_buffer,
#     )
#     await cl.Message(content=output_state["messages"][-1].content, elements=[output_audio_el]).send()


