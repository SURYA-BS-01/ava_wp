from functools import lru_cache
from langgraph.graph import StateGraph
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.nodes import memory_extraction_node, router_node, context_injection_node

@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(AICompanionState)

    graph_builder.add_node("memory_extraction_node", memory_extraction_node)
    graph_builder.add_node("router_node", router_node)
    graph_builder.add_node("context_injection_node", context_injection_node)

# from functools import lru_cache
# from langgraph.graph import StateGraph
# from ai_companion.graph.state import AICompanionState
# from ai_companion.graph.nodes import memory_extraction_node, router_node

# @lru_cache(maxsize=1)
# def create_workflow_graph():
#     graph_builder = StateGraph(AICompanionState)

#     # Add nodes
#     graph_builder.add_node("memory_extraction_node", memory_extraction_node)
#     graph_builder.add_node("router_node", router_node)

#     # Define edges
#     graph_builder.set_entry_point("memory_extraction_node")
#     graph_builder.add_edge("memory_extraction_node", "router_node")

#     # Optionally: end at router_node (you can add more later)
#     graph_builder.set_finish_point("router_node")

#     # Return compiled graph
#     return graph_builder.compile()
