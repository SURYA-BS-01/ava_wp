from ai_companion.graph.state import AICompanionState
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager
from ai_companion.graph.utils.chains import get_router_chain
from ai_companion.settings import settings

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