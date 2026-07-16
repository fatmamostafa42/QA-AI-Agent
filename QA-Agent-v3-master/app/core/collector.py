from datetime import datetime
from typing import Any


class Collector:
    """
    Collects all exploration data generated during the crawl.
    This object becomes the single source of truth for the AI Agent.
    """

    def __init__(self, base_url: str):

        self.data = {
            "application": {
                "base_url": base_url,
                "generated_at": datetime.utcnow().isoformat(),
                "pages_count": 0,
            },
            "pages": [],
            "network": [],
            "screenshots": [],
            "html_snapshots": [],
            "errors": [],
        }

    def add_page(self, page: dict):

        self.data["pages"].append(page)

        self.data["application"]["pages_count"] = len(
            self.data["pages"]
        )

    def add_network_request(self, request: dict):

        self.data["network"].append(request)

    def add_screenshot(self, screenshot: dict):

        self.data["screenshots"].append(screenshot)

    def add_html_snapshot(self, snapshot: dict):

        self.data["html_snapshots"].append(snapshot)

    def add_error(self, error: Any):

        self.data["errors"].append(str(error))

    def export(self) -> dict:

        return self.data
    