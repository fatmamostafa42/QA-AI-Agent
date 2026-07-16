from collections import deque

from app.automation.playwright.explorer import Explorer
from app.core.collector import Collector


class Crawler:
    """
    Crawl the application by visiting all discovered pages.
    """

    def __init__(self, page):
        self.page = page
        self.explorer = Explorer(page)

    def crawl(self, max_pages: int = 30):

        self.explorer.wait_until_ready()

        collector = Collector(self.explorer.base_url)

        queue = deque([self.page.url])

        visited = set()

        while queue and len(visited) < max_pages:

            current_url = queue.popleft()

            if current_url in visited:
                continue

            print(f"[{len(visited)+1}] Visiting: {current_url}")

            try:

                self.page.goto(current_url)

                self.explorer.wait_until_ready()

                page_data = self.explorer.explore()

                collector.add_page(page_data)

                visited.add(current_url)

                for link in page_data["navigation"]["internal_links"]:

                    if (
                        link not in visited
                        and link not in queue
                    ):
                        queue.append(link)

            except Exception as e:

                collector.add_error(e)

        return collector.export()