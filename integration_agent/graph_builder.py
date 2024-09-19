from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph
from integration_agent.models.agent_state import AgentState
from integration_agent.agent import IntegrationAgent

def check_end_condition(state):
    print("Checking end condition", flush=True)
    print(f"State: {state}", flush=True)
    if (
        len(state.get("childToBeProcessedNodes", [])) == 0
        and len(state.get("InProcessNodes", [])) == 0
    ):
        print("Ending execution", flush=True)
        return "end"
    else:
        print("Continuing execution", flush=True)
        return "continue"


# Initialize the IntegrationAgent
def build_graph(har_file_path):
    agent = IntegrationAgent(har_file_path)
    # agent.all_url_list = your_all_url_list  # You need to define this
    # agent.url_to_curl_dict = your_url_to_curl_dict  # You need to define this
    # agent.cookie_dict = your_cookie_dict  # You need to define this

    # Create the graph
    graph_builder = StateGraph(AgentState)

    # Add nodes using the agent's methods
    graph_builder.add_node("IntegrationAgent", agent.url_identify_agent)
    graph_builder.set_entry_point("IntegrationAgent")

    graph_builder.add_node("urlToCurl", agent.url_to_curl)
    graph_builder.add_edge("IntegrationAgent", "urlToCurl")

    graph_builder.add_node(
        "dynamicUrlDataIdentifyingAgent", agent.dynamic_url_data_identifying_agent
    )
    graph_builder.add_edge("urlToCurl", "dynamicUrlDataIdentifyingAgent")

    graph_builder.add_node("findCurlFromContent", agent.find_curl_from_content)
    graph_builder.add_edge("dynamicUrlDataIdentifyingAgent", "findCurlFromContent")

    # Add conditional edges
    graph_builder.add_conditional_edges(
        "findCurlFromContent",
        check_end_condition,
        {"end": END, "continue": "dynamicUrlDataIdentifyingAgent"},
    )

    # Compile the graph
    graph = graph_builder.compile()
    return graph