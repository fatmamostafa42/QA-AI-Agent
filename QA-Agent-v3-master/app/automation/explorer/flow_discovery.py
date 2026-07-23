# flow_discovery.py

from __future__ import annotations

from typing import Dict, List, Optional, Set, Any
from collections import deque


class FlowDiscovery:
    """
    ============================================================
    Flow Graph Engine V3

    Responsible for building a navigation graph for any website.

    Node  = Page

    Edge  = Navigation between two pages

    Generic implementation.

    No application specific logic.

    ============================================================
    """

    def __init__(self):

        # ============================================
        # Graph
        # ============================================

        self.nodes: Dict[str, Dict] = {}

        self.edges: List[Dict] = []

        self.visited: Set[str] = set()

        self.queue = deque()

    # ============================================================
    # Node Management
    # ============================================================

    def add_node(
        self,
        url: str,
        title: str = "",
        page_type: str = "unknown",
        metadata: Optional[Dict] = None,
    ):

        if not url:
            return

        if url in self.nodes:
            return

        self.nodes[url] = {

            "url": url,

            "title": title,

            "page_type": page_type,

            "metadata": metadata or {},

            "parents": [],

            "children": [],

            "actions": [],

            "depth": 0,

            "visited": False,
        }

    # ============================================================
    # Edge Management
    # ============================================================

    def add_edge(
        self,
        source: str,
        target: str,
        action: str = "navigate",
        element: str = "",
        locator: str = "",
    ):

        if not source or not target:
            return

        self.add_node(source)
        self.add_node(target)

        edge = {

            "from": source,

            "to": target,

            "action": action,

            "element": element,

            "locator": locator,
        }

        if edge not in self.edges:
            self.edges.append(edge)

        if target not in self.nodes[source]["children"]:
            self.nodes[source]["children"].append(target)

        if source not in self.nodes[target]["parents"]:
            self.nodes[target]["parents"].append(source)

    # ============================================================
    # Node Information
    # ============================================================

    def update_node(
        self,
        url: str,
        **kwargs
    ):

        if url not in self.nodes:
            self.add_node(url)

        node = self.nodes[url]

        for key, value in kwargs.items():

            node[key] = value

    # ============================================================
    # Actions
    # ============================================================

    def set_actions(
        self,
        url: str,
        actions: List[Dict]
    ):

        if url not in self.nodes:
            self.add_node(url)

        self.nodes[url]["actions"] = actions

    # ============================================================
    # Queue Management
    # ============================================================

    def enqueue(
        self,
        url: str,
        depth: int
    ):

        if url in self.visited:
            return

        self.queue.append(
            (
                url,
                depth
            )
        )

    def dequeue(self):

        if not self.queue:
            return None

        return self.queue.popleft()

    # ============================================================
    # Visited
    # ============================================================

    def mark_visited(
        self,
        url: str
    ):

        self.visited.add(url)

        if url in self.nodes:
            self.nodes[url]["visited"] = True

    def is_visited(
        self,
        url: str
    ) -> bool:

        return url in self.visited

    # ============================================================
    # Queries
    # ============================================================

    def has_node(
        self,
        url: str
    ) -> bool:

        return url in self.nodes

    def get_node(
        self,
        url: str
    ):

        return self.nodes.get(url)

    def get_children(
        self,
        url: str
    ) -> List[str]:

        if url not in self.nodes:
            return []

        return self.nodes[url]["children"]

    def get_parents(
        self,
        url: str
    ) -> List[str]:

        if url not in self.nodes:
            return []

        return self.nodes[url]["parents"]

    # ============================================================
    # Statistics
    # ============================================================

    def total_nodes(self):

        return len(self.nodes)

    def total_edges(self):

        return len(self.edges)

    def clear(self):

        self.nodes.clear()

        self.edges.clear()

        self.visited.clear()

        self.queue.clear()

    # ============================================================
# State Management
# ============================================================

def build_state_key(
    self,
    page_info: Dict
) -> str:
    """
    Build a unique state signature for the page.

    The goal is to distinguish between different page states
    without relying only on the URL.
    """

    url = page_info.get("url", "")

    page_type = page_info.get("page_type", "")

    title = page_info.get("title", "")

    actions = page_info.get("actions", [])

    action_names = sorted(
        [
            action.get("action", "")
            for action in actions
            if isinstance(action, dict)
        ]
    )

    return "|".join(
        [
            url,
            page_type,
            title,
            ",".join(action_names),
        ]
    )


# ============================================================
# Duplicate Detection
# ============================================================

def is_duplicate_state(
    self,
    page_info: Dict
) -> bool:

    state = self.build_state_key(page_info)

    for node in self.nodes.values():

        metadata = node.get("metadata", {})

        if not metadata:
            continue

        existing = metadata.get("state_key")

        if existing == state:
            return True

    return False


# ============================================================
# Register State
# ============================================================

def register_state(
    self,
    page_info: Dict
):

    url = page_info.get("url")

    if not url:
        return

    state = self.build_state_key(page_info)

    if url not in self.nodes:
        self.add_node(url)

    self.nodes[url]["metadata"]["state_key"] = state


# ============================================================
# Loop Detection
# ============================================================

def creates_loop(
    self,
    source: str,
    target: str
) -> bool:
    """
    Prevent simple navigation loops.
    """

    if source == target:
        return True

    if target in self.get_parents(source):
        return True

    return False


# ============================================================
# Safe Edge
# ============================================================

def safe_add_edge(
    self,
    source: str,
    target: str,
    action: str = "navigate",
    element: str = "",
    locator: str = "",
):

    if self.creates_loop(source, target):
        return

    self.add_edge(
        source,
        target,
        action,
        element,
        locator,
    )


# ============================================================
# Discover New State
# ============================================================

def discover_state(
    self,
    page_info: Dict
) -> bool:
    """
    Returns True if the page is a new state.
    """

    if self.is_duplicate_state(page_info):
        return False

    self.register_state(page_info)

    return True


# ============================================================
# Next Pages
# ============================================================

def discover_next_pages(
    self,
    current_url: str,
    links: List[str],
    depth: int
):

    for link in links:

        if not link:
            continue

        if self.is_visited(link):
            continue

        self.safe_add_edge(
            current_url,
            link,
        )

        self.enqueue(
            link,
            depth + 1,
        )    

# ============================================================
# Flow Discovery
# ============================================================

def discover_flow(
    self,
    current_page: Dict,
    navigation: Dict,
):
    """
    Discover navigation flow from current page.

    Parameters
    ----------
    current_page : dict
        Current page information.

    navigation : dict
        Navigation scanner output.
    """

    current_url = current_page.get("url", "")

    if not current_url:
        return

    self.add_node(
        url=current_url,
        title=current_page.get("title", ""),
        page_type=current_page.get("page_type", "unknown"),
        metadata=current_page,
    )

    self.register_state(current_page)

    actions = current_page.get("actions", [])

    self.set_actions(
        current_url,
        actions,
    )

    internal_links = navigation.get(
        "internal_links",
        [],
    )

    for target in internal_links:

        if not target:
            continue

        self.safe_add_edge(
            source=current_url,
            target=target,
            action="navigate",
        )


# ============================================================
# Navigation Graph Builder
# ============================================================

def build_graph(
    self,
    page_result: Dict,
):
    """
    Build graph using one crawler result.
    """

    page = page_result.get("page", {})

    navigation = page_result.get(
        "navigation",
        {},
    )

    self.discover_flow(
        page,
        navigation,
    )


# ============================================================
# Connected Components
# ============================================================

def get_connected_pages(
    self,
    url: str,
):

    if url not in self.nodes:
        return []

    result = set()

    stack = [url]

    while stack:

        current = stack.pop()

        if current in result:
            continue

        result.add(current)

        children = self.get_children(current)

        parents = self.get_parents(current)

        stack.extend(children)

        stack.extend(parents)

    return list(result)


# ============================================================
# Root Pages
# ============================================================

def get_root_pages(self):

    roots = []

    for url, node in self.nodes.items():

        if len(node["parents"]) == 0:

            roots.append(url)

    return roots


# ============================================================
# Leaf Pages
# ============================================================

def get_leaf_pages(self):

    leaves = []

    for url, node in self.nodes.items():

        if len(node["children"]) == 0:

            leaves.append(url)

    return leaves


# ============================================================
# Flow Summary
# ============================================================

def get_summary(self):

    return {

        "nodes": self.total_nodes(),

        "edges": self.total_edges(),

        "roots": len(self.get_root_pages()),

        "leaves": len(self.get_leaf_pages()),

        "visited": len(self.visited),

    }

    # ==========================================================
    # Breadth First Search
    # ==========================================================

def bfs(self, start_node: str):
        """
        Traverse graph using Breadth First Search.
        """

        if start_node not in self.graph:
            return []

        visited = set()
        queue = [start_node]
        order = []

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

        return order

    # ==========================================================
    # Depth First Search
    # ==========================================================

def dfs(self, start_node: str):
        """
        Traverse graph using Depth First Search.
        """

        if start_node not in self.graph:
            return []

        visited = set()
        stack = [start_node]
        order = []

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            neighbors = list(self.graph[current])
            neighbors.reverse()

            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append(neighbor)

        return order

    # ==========================================================
    # Reachability
    # ==========================================================

def reachable_nodes(self, start_node: str):
        """
        Return every node reachable from start node.
        """

        return self.bfs(start_node)

    # ==========================================================
    # Path Search
    # ==========================================================

def path_exists(
        self,
        source: str,
        destination: str
    ):
        """
        Returns True if destination is reachable.
        """

        if source == destination:
            return True

        visited = set()
        queue = [source]

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            for nxt in self.graph.get(current, []):

                if nxt == destination:
                    return True

                if nxt not in visited:
                    queue.append(nxt)

        return False

    # =====================================================
    # Shortest Path (BFS)
    # =====================================================

def shortest_path(
    self,
    start: str,
    target: str
) -> List[str]:

    if start not in self.graph:
            return []

    queue = deque([[start]])
    visited = {start}

    while queue:

            path = queue.popleft()
            node = path[-1]

            if node == target:
               return path

            for nxt in self.graph.get(node, []):

                if nxt in visited:
                 continue

                visited.add(nxt)
                queue.append(path + [nxt])

    return []

    # ==========================================================
    # Export Graph
    # ==========================================================

def export_json(self) -> Dict[str, Any]:
       """
       Export graph as serializable json.
       """

       return {
           "pages": sorted(list(self.nodes)),
           "edges": [
               {
                  "from": source,
                  "to": target
               }
               for source, targets in self.graph.items()
               for target in sorted(targets)
            ]
        }

    # ==========================================================
    # Statistics
    # ==========================================================

def statistics(self) -> Dict[str, Any]:
        """
        Graph statistics.
        """

        edge_count = sum(
            len(v)
            for v in self.graph.values()
        )

        return {
            "pages": len(self.nodes),
            "edges": edge_count,
            "roots": len(self.find_roots()),
            "leaves": len(self.find_leaves()),
            "cycles": len(self.detect_cycles())
        }

    # ==========================================================
    # Generic Utilities
    # ==========================================================

def has_node(
           self,
           node: str
        ) -> bool:

            return node in self.nodes

def has_edge(
           self,
           source: str,
           target: str
        ) -> bool:

            return target in self.graph.get(
                source,
                set()
            )

def neighbors(
           self,
           node: str
        ) -> List[str]:

            return sorted(
                self.graph.get(
                    node,
                    set()
                )
            )

def incoming(
            self,
            node: str
        ) -> List[str]:

            result = []

            for source, targets in self.graph.items():

                if node in targets:

                    result.append(source)

            return sorted(result)

def outgoing(
            self,
            node: str
        ) -> List[str]:

           return self.neighbors(node)


def clear(self):

        self.graph.clear()
        self.reverse_graph.clear()
        self.nodes.clear()

def merge(
        self,
        other: "FlowDiscovery"
    ):

        for node in other.nodes:

            self.nodes.add(node)

        for source, targets in other.graph.items():

            for target in targets:

                self.add_transition(
                    source,
                    target
                )