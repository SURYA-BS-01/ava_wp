from functools import lru_cache
from langgraph.graph import StateGraph
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.nodes import (
    memory_extraction_node,
    router_node,
    context_injection_node,
    memory_injection_node,
    image_node,
    conversation_node,
    audio_node
)

@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(AICompanionState)

    graph_builder.add_node("memory_extraction_node", memory_extraction_node)
    graph_builder.add_node("router_node", router_node)
    graph_builder.add_node("context_injection_node", context_injection_node)
    graph_builder.add_node("memory_injection_node", memory_injection_node)
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("image_node", image_node)
    graph_builder.add_node("audio_node", audio_node)