from ai_companion.graph.state import AICompanionState
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager

async def memory_extraction_node(state: AICompanionState):
    """Extract and store important information from the last message."""
    if not state["messages"]:
        return {}
    
    memory_manager = get_memory_manager()
    await memory_manager.extract_and_store_memories(state["messages"][-1])
    return {}