from typing import List
from integration_agent.graph_builder import build_graph

async def call_agent(har_file_path: str, max_steps: int = 8):
    graph = build_graph(har_file_path)
    event_stream = graph.astream(
        {
            "masterNode": None,
            "inProcessNode": None,
            "InProcessNodes": [],
            "childToBeProcessedNodes": [],
            "searchString": [],
            # "allUrlList": listOfUrls,
            "downloadUrl": "",
        },
        {
            "recursion_limit": max_steps,
        },
    )
    async for event in event_stream:
        print("+++", event)
