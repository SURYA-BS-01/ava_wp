import os
from uuid import uuid4

from ai_companion.graph.state import AICompanionState
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager
from ai_companion.graph.utils.chains import get_router_chain, get_character_response_chain
from ai_companion.settings import settings
from ai_companion.modules.schedules.context_generation import ScheduleContextGenerator
from ai_companion.graph.utils.helpers import get_text_to_image_module, get_text_to_speech_module, get_chat_model

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

async def memory_extraction_node(state: AICompanionState):
    """Extract and store important information from the last message."""
    if not state["messages"]:
        return {}
    
    memory_manager = get_memory_manager()
    await memory_manager.extract_and_store_memories(state["messages"][-1])
    return {}

async def router_node(state: AICompanionState):
    chain = get_router_chain()
    response = await chain.ainvoke({"messages": state["messages"][-settings.ROUTER_MESSAGES_TO_ANALYZE: ]})
    return {"workflow": response.response_type}

def context_injection_node(state: AICompanionState):
    schedule_context = ScheduleContextGenerator.get_current_activity()
    if schedule_context != state.get("current_activity", " "):
        apply_activity = True
    else:
        apply_activity = False
    return {"apply_activity": apply_activity, "current_activity": schedule_context}

def memory_injection_node(state: AICompanionState):
    memory_manager = get_memory_manager()

    recent_context = " ".join([m.content for m in state["messages"][-3:]])
    memories = memory_manager.get_relevant_memories(recent_context)

    memory_context = memory_manager.format_memories_for_prompt(memories)

    return {"memory_context": memory_context}

async def conversation_node(state: AICompanionState, config: RunnableConfig):
    current_activity = ScheduleContextGenerator.get_current_activity()
    memory_context = state.get("memory_context", "")

    chain =  get_character_response_chain(state.get("summary", ""))

    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "current_activity": current_activity,
            "memory_context": memory_context,
        },
        config=config
    )

    return {"messages": AIMessage(content=response)}
    

async def image_node(state: AICompanionState, config: RunnableConfig):
    current_activity = ScheduleContextGenerator.get_current_activity()
    memory_context = state.get("memory_context")

    chain = get_character_response_chain(state.get("summary", ""))
    text_to_image_module = get_text_to_image_module()

    scenario = await text_to_image_module.create_scenario(state["messages"][-5:])

    os.makedirs("generated_images", exist_ok=True)
    img_path = f"generated_images/image_{str(uuid4())}.png"

    text_to_image_module.generate_image(scenario.image_prompt, img_path)

    scenario_message = HumanMessage(content=f"<image attached by Ava generated from prompt: {scenario.image_prompt} + \ndont say like you did not generate an image or You're not able to generate an image d>")
    updated_messages = state["messages"] + [scenario_message]

    response = await chain.ainvoke(
        {
            "messages": updated_messages,
            "current_activity": current_activity,
            "memory_context": memory_context,
        },
        config,
    )
    return {"messages": AIMessage(content=response), "image_path": img_path}

async def audio_node(state: AICompanionState, config: RunnableConfig):
    current_activity = ScheduleContextGenerator.get_current_activity()
    memory_context = state.get("memory_context", "")

    chain = get_character_response_chain(state.get("summary", ""))
    text_to_speech_module = get_text_to_speech_module()

    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "current_activity": current_activity,
            "memory_context": memory_context,
        },
        config=config
    )

    output_audio = await text_to_speech_module.synthesize(response)

    return {"messages": response, "audio_buffer": output_audio}

async def summarize_conversation_node(state: AICompanionState):
    model = get_chat_model()
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date between Ava and the user: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = (
            "Create a summary of the conversation above between Ava and the user. "
            "The summary must be a short description of the conversation so far, "
            "but that captures all the relevant information shared between Ava and the user:"
        )

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = await model.ainvoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][: -settings.TOTAL_MESSAGES_AFTER_SUMMARY]]

    return {"summary": response.content, "messages": delete_messages}