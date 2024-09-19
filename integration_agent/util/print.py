from integration_agent.models.tree_map import TreeNode

def print_tree(node: TreeNode, prefix: str = "", is_last: bool = True):
    """
    Recursively prints the tree structure with visual connectors.
    Args:
    node (TreeNode): The current node to print
    prefix (str): The prefix string for the current line
    is_last (bool): Whether the current node is the last child of its parent
    """
    # Prepare the connector and new prefix for children
    connector = "└── " if is_last else "├── "
    new_prefix = prefix + ("    " if is_last else "│   ")

    # Print the current node
    print(f"{prefix}{connector}{node}")

    # Recursively print all children
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        is_last_child = i == child_count - 1
        print_tree(child, new_prefix, is_last_child)