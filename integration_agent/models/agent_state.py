from typing import List, Optional, TypedDict
from integration_agent.models.tree_map import TreeNode


class AgentState(TypedDict):
    masterNode: TreeNode  # User request
    inProcessNode: TreeNode
    InProcessNodes: List[TreeNode]
    childToBeProcessedNodes: List[TreeNode]
    # to find the cUrl
    searchString: List[str]
    # allUrlList: List[str]
    downloadUrl: str
