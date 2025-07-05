import asyncio
from langchain_core.messages import HumanMessage
from ai_companion.graph.state import AICompanionState
from ai_companion.graph.graph import create_workflow_graph

from dotenv import load_dotenv
load_dotenv(".env")  # Or use the full path if needed

async def main():
    # Create a test message
    messages = [HumanMessage(content="I adopted a dog named Max last weekend.")]
    
    # Set up initial state
    state = AICompanionState(
        messages=messages,
        summary="",
        workflow="conversation",
        audio_buffer=b"",
        image_path="",
        current_activity="",
        apply_activity=False,
        memory_context=""
    )

    # Build the graph
    graph = create_workflow_graph()
    
    # Run the graph
    final_state = await graph.ainvoke(state)

    # Print result
    print("Final State:")
    print(final_state)

if __name__ == "__main__":
    asyncio.run(main())
