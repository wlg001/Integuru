from typing import List, Optional


class TreeNode:
    def __init__(
        self,
        cUrl: Optional[str] = None,
        cookie: Optional[dict] = None,
        description: Optional[str] = None,
    ):
        self.cUrl = cUrl
        self.cookie = cookie
        self.children: List["TreeNode"] = []
        self.description = description

    def add_child_list_cUrl(
        self, datas
    ):  #: List[Tuple[str, str]]) -> List['TreeNode']:
        # index 0 = cUrl and index 1 = description
        new_children = []
        for data in datas:
            child = TreeNode(cUrl=data)  # [0] , description=data[1])
            self.add_child(child)
            new_children.append(child)
        return new_children

    def add_child_list_cookie(
        self, datas
    ):  # : List[Tuple[str, str]]) -> List['TreeNode']:
        # index 0 = cUrl and index 1 = description
        new_children = []
        for data in datas:
            child = TreeNode(cUrl=data)  # [0] , description=data[1])
            self.add_child(child)
            new_children.append(child)
        return new_children

    def add_child(self, child: "TreeNode") -> None:
        self.children.append(child)

    def __str__(self):

        if self.cUrl:
            return f"{self.description} \n {self.cUrl}"
        if self.cookie:
            return f"{self.description} \n {self.cookie}"
        else:
            return "Empty TreeNode"
