class StateManager:
    """
    Keeps track of visited pages and discovered application states.
    """

    def __init__(self):
        self.visited_urls = set()
        self.page_states = {}

    def is_visited(self, url: str) -> bool:
        return url in self.visited_urls

    def mark_visited(self, url: str):
        self.visited_urls.add(url)

    def save_state(self, url: str, state: dict):
        self.page_states[url] = state

    def get_state(self, url: str):
        return self.page_states.get(url)

    def reset(self):
        self.visited_urls.clear()
        self.page_states.clear()