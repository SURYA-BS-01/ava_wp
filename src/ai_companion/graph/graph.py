from functools import lru_cache
from langgraph.graph import StateGraph, START, END
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.nodes import (
    memory_extraction_node,
    router_node,
    context_injection_node,
    memory_injection_node,
    image_node,
    conversation_node,
    audio_node,
    summarize_conversation_node
)
from ai_companion.graph.edges import select_workflow, should_summarize_conversation

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
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)

    graph_builder.add_edge(START, "memory_extraction_node")
    graph_builder.add_edge("memory_extraction_node", "router_node")

    graph_builder.add_edge("router_node", "context_injection_node")
    graph_builder.add_edge("context_injection_node", "memory_injection_node")

    graph_builder.add_conditional_edges("memory_injection_node", select_workflow)

    graph_builder.add_conditional_edges("conversation_node", should_summarize_conversation)
    graph_builder.add_conditional_edges("image_node", should_summarize_conversation)
    graph_builder.add_conditional_edges("audio_node", should_summarize_conversation)
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder

graph = create_workflow_graph().compile()