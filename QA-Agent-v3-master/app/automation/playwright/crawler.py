from collections import deque
from urllib.parse import urlparse, urljoin
import re

from app.automation.playwright.explorer import Explorer
from app.core.collector import Collector


class Crawler:
    """
    Generic Web Application Crawler

    Responsibilities:
    - Discover application pages
    - Handle SPA navigation
    - Prevent infinite loops
    - Detect redirects
    - Collect exploration data
    """

    def __init__(self, page):

        self.page = page

        self.explorer = Explorer(page)

        parsed = urlparse(page.url)

        self.base_domain = parsed.netloc
        self.base_scheme = parsed.scheme

        self.blocked_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".css",
            ".js",
            ".woff",
            ".woff2",
            ".ico",
            ".pdf",
            ".zip",
            ".mp4",
            ".mp3",
            ".avi"
        }

        self.authentication_patterns = [
            "/login",
            "/signin",
            "/sign-in",
            "/auth",
            "/authenticate",
            "/authentication",
            "/account/login",
            "/user/login",
            "/session"
        ]

        self.default_max_depth = 5

        # Pages already explored
        self.visited_urls = set()

        # Fingerprints already explored
        self.visited_fingerprints = set()

        # Fingerprints already queued
        self.queued_fingerprints = set()

    # =====================================================
    # MAIN CRAWLER
    # =====================================================

    def crawl(
        self,
        max_pages=None,
        max_depth=None
    ):

        self.explorer.wait_until_ready()

        collector = Collector(
            self.explorer.base_url
        )

        if max_depth is None:
            max_depth = self.default_max_depth

        queue = deque()

        start_url = self.normalize_url(
            self.page.url
        )

        if not start_url:
            return collector.export()

        queue.append({
            "url": start_url,
            "depth": 0
        })

        self.queued_fingerprints.add(
            self.get_url_fingerprint(start_url)
        )

        page_counter = 0

        while queue:

            item = queue.popleft()

            requested_url = item["url"]
            depth = item["depth"]

            fingerprint = self.get_url_fingerprint(
                requested_url
            )

            self.queued_fingerprints.discard(
                fingerprint
            )

            if not requested_url:
                continue

            if depth > max_depth:
                continue

            if fingerprint in self.visited_fingerprints:
                continue

            if requested_url in self.visited_urls:
                continue

            page_counter += 1

            print(
                f"\n[{page_counter}] Visiting: {requested_url}"
            )

            print(
                f"Depth: {depth}"
            )

            try:

                self.page.goto(
                    requested_url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                self.explorer.wait_until_ready()

                final_url = self.normalize_url(
                    self.page.url
                )

                if not final_url:
                    continue

                final_fingerprint = (
                    self.get_url_fingerprint(
                        final_url
                    )
                )

                if final_fingerprint in self.visited_fingerprints:
                    continue

                if final_url in self.visited_urls:
                    continue

                redirect_info = self.detect_redirect(
                    requested_url,
                    final_url
                )

                page_data = self.explorer.explore()

                page_data["page"]["requested_url"] = requested_url
                page_data["page"]["final_url"] = final_url
                page_data["page"]["crawl_depth"] = depth

                page_data["page"].update(
                    redirect_info
                )

                collector.add_page(
                    page_data
                )

                self.visited_urls.add(
                    final_url
                )

                self.visited_fingerprints.add(
                    final_fingerprint
                )

                if redirect_info.get(
                    "redirect_reason"
                ) == "authentication_required":

                    print(
                        "Authentication page detected - skipping children"
                    )

                    continue

                navigation = page_data.get(
                    "navigation",
                    {}
                )

                links = navigation.get(
                    "internal_links",
                    []
                )

                print(
                    f"FOUND LINKS: {len(links)}"
                )

                for link in links:

                    normalized = self.normalize_url(
                        link
                    )

                    if not normalized:
                        continue

                    link_fingerprint = (
                        self.get_url_fingerprint(
                            normalized
                        )
                    )

                    if link_fingerprint in self.visited_fingerprints:
                        continue

                    if link_fingerprint in self.queued_fingerprints:
                        continue

                    queue.append({
                        "url": normalized,
                        "depth": depth + 1
                    })

                    self.queued_fingerprints.add(
                        link_fingerprint
                    )

                print(
                    f"QUEUE SIZE: {len(queue)}"
                )

                if max_pages and len(self.visited_urls) >= max_pages:
                    break

            except Exception as e:

                print(
                    f"ERROR crawling {requested_url}: {e}"
                )

                collector.add_error(e)

        print("\n==============================")
        print(f"Total pages crawled: {len(self.visited_urls)}")
        print("==============================")

        return collector.export()
        # =====================================================
    # REDIRECT DETECTION
    # =====================================================

    def detect_redirect(
        self,
        requested_url,
        final_url
    ):

        result = {
            "redirected": requested_url != final_url,
            "redirect_reason": None
        }

        if not result["redirected"]:
            return result

        lower_url = final_url.lower()

        for pattern in self.authentication_patterns:

            if pattern in lower_url:

                result["redirect_reason"] = (
                    "authentication_required"
                )

                return result

        result["redirect_reason"] = (
            "application_redirect"
        )

        return result


    # =====================================================
    # URL NORMALIZATION
    # =====================================================

    def normalize_url(
        self,
        url
    ):

        try:

            if not url:
                return None

            absolute = urljoin(
                self.page.url,
                url
            )

            parsed = urlparse(
                absolute
            )

            # Ignore external domains
            if parsed.netloc != self.base_domain:
                return None

            path = parsed.path

            # Remove duplicated slashes
            path = re.sub(
                r"/+",
                "/",
                path
            )

            # Remove trailing slash
            path = path.rstrip("/")

            if not path:
                path = "/"

            lower_path = path.lower()

            # Ignore static resources
            for ext in self.blocked_extensions:

                if lower_path.endswith(ext):
                    return None

            # Remove fragment (#...)
            fragmentless = (
                f"{self.base_scheme}://"
                f"{parsed.netloc}"
                f"{path}"
            )

            return fragmentless

        except Exception:

            return None
            # =====================================================
    # URL FINGERPRINT
    # =====================================================

    def get_url_fingerprint(
        self,
        url
    ):
        """
        Create a generic fingerprint for dynamic URLs.

        Examples

        /employee/7
        /employee/15
        -> /employee/{id}

        /user/10/profile
        /user/20/profile
        -> /user/{id}/profile
        """

        if not url:
            return None

        parsed = urlparse(
            url
        )

        path = parsed.path.lower()

        # Replace numeric IDs
        path = re.sub(
            r"/\d+",
            "/{id}",
            path
        )

        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-fA-F]{8}-[0-9a-fA-F\-]{27,}",
            "/{uuid}",
            path
        )

        # OrangeHRM style
        path = re.sub(
            r"empnumber/\d+",
            "empnumber/{id}",
            path,
            flags=re.IGNORECASE
        )

        path = re.sub(
            r"candidateid/\d+",
            "candidateid/{id}",
            path,
            flags=re.IGNORECASE
        )

        path = re.sub(
            r"vacancyid/\d+",
            "vacancyid/{id}",
            path,
            flags=re.IGNORECASE
        )

        path = re.sub(
            r"id/\d+",
            "id/{id}",
            path,
            flags=re.IGNORECASE
        )

        return f"{parsed.netloc}{path}"