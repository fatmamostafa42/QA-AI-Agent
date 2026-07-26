# flow_discovery.py

from __future__ import annotations

from typing import Dict, List, Optional, Set, Any
from collections import deque




class FlowDiscovery:
    """
    ===========================================================
    Generic Flow Discovery Engine V4

    Responsibilities
    ----------------
    - Build navigation graph
    - Track page states
    - Discover user journeys
    - Prevent loops
    - Find paths
    - Extract reusable flows

    Generic implementation.

    No application specific logic.
    ===========================================================
    """

    def __init__(self):

        # ------------------------------------
        # Graph
        # ------------------------------------

        self.nodes: Dict[str, Dict[str, Any]] = {}

        self.edges: List[Dict[str, Any]] = []

        # ------------------------------------
        # Crawl State
        # ------------------------------------

        self.visited: Set[str] = set()

        self.queue = deque()

    # ===========================================================
    # Node Management
    # ===========================================================

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

            "visited": False,

            "depth": 0

        }

    def update_node(
        self,
        url: str,
        **kwargs
    ):

        if url not in self.nodes:
            self.add_node(url)

        self.nodes[url].update(kwargs)

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
    # ===========================================================
    # Edge Management
    # ===========================================================

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
        
        print(f"ADD EDGE: {source} ---> {target}")
        
        self.add_node(source)
        self.add_node(target)

        edge = {

            "from": source,

            "to": target,

            "action": action,

            "element": element,

            "locator": locator

        }

        if edge in self.edges:
            return

        self.edges.append(edge)

        if target not in self.nodes[source]["children"]:
            self.nodes[source]["children"].append(target)

        if source not in self.nodes[target]["parents"]:
            self.nodes[target]["parents"].append(source)

    def has_edge(
        self,
        source: str,
        target: str
    ) -> bool:

        for edge in self.edges:

            if (
                edge["from"] == source
                and
                edge["to"] == target
            ):
                return True

        return False

    # ===========================================================
    # Children / Parents
    # ===========================================================

    def get_children(
        self,
        url: str
    ) -> List[str]:

        if url not in self.nodes:
            return []

        return list(
            self.nodes[url]["children"]
        )

    def get_parents(
        self,
        url: str
    ) -> List[str]:

        if url not in self.nodes:
            return []

        return list(
            self.nodes[url]["parents"]
        )

    # ===========================================================
    # Actions
    # ===========================================================

    def set_actions(
        self,
        url: str,
        actions: List[Dict]
    ):

        if url not in self.nodes:
            self.add_node(url)

        self.nodes[url]["actions"] = actions

    def get_actions(
        self,
        url: str
    ) -> List[Dict]:

        if url not in self.nodes:
            return []

        return self.nodes[url]["actions"]

    # ===========================================================
    # Queue
    # ===========================================================

    def enqueue(
        self,
        url: str,
        depth: int
    ):

        if self.is_visited(url):
            return

        self.queue.append({

            "url": url,

            "depth": depth

        })

    def dequeue(self):

        if not self.queue:
            return None

        return self.queue.popleft()

    def queue_size(self):

        return len(self.queue)

    # ===========================================================
    # Visited
    # ===========================================================

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

    # ===========================================================
    # Graph Queries
    # ===========================================================

    def neighbors(
        self,
        url: str
    ) -> List[str]:

        return self.get_children(url)

    def incoming(
        self,
        url: str
    ) -> List[str]:

        return self.get_parents(url)

    def outgoing(
        self,
        url: str
    ) -> List[str]:

        return self.get_children(url)
        # ===========================================================
    # State Management
    # ===========================================================

    def build_state_key(
        self,
        page_info: Dict
    ) -> str:
        """
        Build a unique page state signature.
        """

        url = page_info.get("url", "")

        page_type = page_info.get(
            "page_type",
            ""
        )

        title = page_info.get(
            "title",
            ""
        )

        actions = page_info.get(
            "actions",
            []
        )

        action_names = sorted(

            action.get("action", "")

            for action in actions

            if isinstance(action, dict)

        )

        return "|".join([

            url,

            page_type,

            title,

            ",".join(action_names)

        ])

    def register_state(
        self,
        page_info: Dict
    ):

        url = page_info.get("url")

        if not url:
            return

        if url not in self.nodes:
            self.add_node(url)

        self.nodes[url]["metadata"]["state_key"] = (

            self.build_state_key(page_info)

        )

    def is_duplicate_state(
        self,
        page_info: Dict
    ) -> bool:

        state_key = self.build_state_key(
            page_info
        )

        for node in self.nodes.values():

            metadata = node.get(
                "metadata",
                {}
            )

            if metadata.get(
                "state_key"
            ) == state_key:

                return True

        return False

    def discover_state(
        self,
        page_info: Dict
    ) -> bool:

        if self.is_duplicate_state(
            page_info
        ):
            return False

        self.register_state(
            page_info
        )

        return True

    # ===========================================================
    # Loop Protection
    # ===========================================================

    def creates_loop(
        self,
        source: str,
        target: str
    ) -> bool:

        if source == target:
            return True

        if target in self.get_parents(source):
            return True

        return False

    def safe_add_edge(
        self,
        source: str,
        target: str,
        action: str = "navigate",
        element: str = "",
        locator: str = ""
    ):

        if self.creates_loop(
            source,
            target
        ):
            return

        self.add_edge(

            source,

            target,

            action,

            element,

            locator

        )

    # ===========================================================
    # Flow Discovery
    # ===========================================================

    def discover_flow(
        self,
        current_page: Dict,
        navigation: Dict
    ):

        current_url = current_page.get(
            "url",
            ""
        )

        if not current_url:
            return

        self.add_node(

            url=current_url,

            title=current_page.get(
                "title",
                ""
            ),

            page_type=current_page.get(
                "page_type",
                "unknown"
            ),

            metadata=current_page

        )

        self.register_state(
            current_page
        )

        actions = current_page.get(
            "actions",
            []
        )

        self.set_actions(
            current_url,
            actions
        )

        internal_links = navigation.get(
            "internal_links",
            []
        )

        for link in internal_links:

            if not link:
                continue

            self.safe_add_edge(

                source=current_url,

                target=link,

                action="navigate"

            )

    # ===========================================================
    # Build Graph
    # ===========================================================

    def build_graph(
        self,
        page_result: Dict
    ):

        self.discover_flow(

            page_result.get(
                "page",
                {}
            ),

            page_result.get(
                "navigation",
                {}
            )

        )
            # ===========================================================
    # Breadth First Search
    # ===========================================================

    def bfs(
        self,
        start: str
    ) -> List[str]:

        if start not in self.nodes:
            return []

        visited = set()
        queue = deque([start])
        order = []

        while queue:

            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            for neighbor in self.get_children(current):

                if neighbor not in visited:
                    queue.append(neighbor)

        return order

    # ===========================================================
    # Depth First Search
    # ===========================================================

    def dfs(
        self,
        start: str
    ) -> List[str]:

        if start not in self.nodes:
            return []

        visited = set()
        stack = [start]
        order = []

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            neighbors = list(
                self.get_children(current)
            )

            neighbors.reverse()

            for neighbor in neighbors:

                if neighbor not in visited:
                    stack.append(neighbor)

        return order

    # ===========================================================
    # Reachability
    # ===========================================================

    def reachable_nodes(
        self,
        start: str
    ) -> List[str]:

        return self.bfs(start)

    # ===========================================================
    # Path Search
    # ===========================================================

    def path_exists(
        self,
        source: str,
        target: str
    ) -> bool:

        return len(
            self.shortest_path(
                source,
                target
            )
        ) > 0

    # ===========================================================
    # Shortest Path
    # ===========================================================

    def shortest_path(
        self,
        start: str,
        target: str
    ) -> List[str]:

        if start not in self.nodes:
            return []

        queue = deque([[start]])
        visited = {start}

        while queue:

            path = queue.popleft()
            node = path[-1]

            if node == target:
                return path

            for neighbor in self.get_children(node):

                if neighbor in visited:
                    continue

                visited.add(neighbor)
                queue.append(path + [neighbor])

        return []

    # ===========================================================
    # Cycle Detection
    # ===========================================================

    def detect_cycles(self) -> List[List[str]]:

        cycles = []

        visited = set()
        recursion = set()

        def visit(node, path):

            visited.add(node)
            recursion.add(node)

            for neighbor in self.get_children(node):

                if neighbor not in visited:

                    visit(
                        neighbor,
                        path + [neighbor]
                    )

                elif neighbor in recursion:

                    try:

                        idx = path.index(neighbor)

                        cycles.append(path[idx:])

                    except ValueError:

                        pass

            recursion.remove(node)

        for node in self.nodes:

            if node not in visited:

                visit(node, [node])

        return cycles

    # ===========================================================
    # Flow Extraction
    # ===========================================================

    def extract_flows(self) -> List[Dict[str, Any]]:
        """
        Extract reusable user journeys from the graph.
        """

        flows = []
        print("\n========== GRAPH DEBUG ==========")
        print("Nodes:", len(self.nodes))
        print("Edges:", len(self.edges))
        print("Roots:", self.get_root_pages())
        print("Leaves:", self.get_leaf_pages())
        print("=================================\n")

        roots = self.get_root_pages()

        if not roots and self.nodes:
            roots = [next(iter(self.nodes.keys()))]

        for root in roots:

            leaves = self.get_leaf_pages()

            if not leaves:
                leaves = [root]

            for leaf in leaves:

                path = self.shortest_path(
                    root,
                    leaf
                )
                print("PATH:", root, "->", leaf, "=", path)

                if len(path) <= 1:
                    continue

                actions = []

                for i in range(len(path) - 1):

                    source = path[i]
                    target = path[i + 1]

                    edge = next(

                        (
                            e
                            for e in self.edges
                            if (
                                e["from"] == source
                                and
                                e["to"] == target
                            )
                        ),

                        None

                    )

                    if edge:
                        actions.append(edge)

                flows.append({

                    "name": f"{path[0]} -> {path[-1]}",

                    "pages": path,

                    "actions": actions,

                    "length": len(path)

                })

        return flows

    # ===========================================================
    # Statistics
    # ===========================================================

    def total_nodes(self):

        return len(self.nodes)

    def total_edges(self):

        return len(self.edges)

    def get_root_pages(self) -> List[str]:

        return [

            url

            for url, node in self.nodes.items()

            if len(node["parents"]) == 0

        ]

    def get_leaf_pages(self) -> List[str]:

        return [

            url

            for url, node in self.nodes.items()

            if len(node["children"]) == 0

        ]

    def statistics(self) -> Dict[str, Any]:

        return {

            "pages": self.total_nodes(),

            "edges": self.total_edges(),

            "roots": len(self.get_root_pages()),

            "leaves": len(self.get_leaf_pages()),

            "cycles": len(self.detect_cycles()),

            "visited": len(self.visited)

        }

    # ===========================================================
    # Export / Import
    # ===========================================================

    def export_json(self) -> Dict[str, Any]:

        return {

            "nodes": list(self.nodes.values()),

            "edges": self.edges,

            "statistics": self.statistics()

        }

    def import_json(
        self,
        data: Dict[str, Any]
    ):

        self.clear()

        for node in data.get("nodes", []):

            self.add_node(

                url=node.get("url", ""),

                title=node.get("title", ""),

                page_type=node.get(
                    "page_type",
                    "unknown"
                ),

                metadata=node.get(
                    "metadata",
                    {}
                )

            )

        for edge in data.get("edges", []):

            self.add_edge(

                edge.get("from", ""),

                edge.get("to", ""),

                edge.get("action", "navigate"),

                edge.get("element", ""),

                edge.get("locator", "")

            )

    # ===========================================================
    # Utilities
    # ===========================================================

    def merge(
        self,
        other: "FlowDiscovery"
    ):

        for node in other.nodes.values():

            self.add_node(

                url=node["url"],

                title=node.get("title", ""),

                page_type=node.get(
                    "page_type",
                    "unknown"
                ),

                metadata=node.get(
                    "metadata",
                    {}
                )

            )

        for edge in other.edges:

            self.add_edge(

                edge["from"],

                edge["to"],

                edge.get("action", "navigate"),

                edge.get("element", ""),

                edge.get("locator", "")

            )

    def clear(self):

        self.nodes.clear()
        self.edges.clear()
        self.visited.clear()
        self.queue.clear()

    # ===========================================================
    # End
    # ===========================================================