from collections import deque
from urllib.parse import urlparse, urljoin
import re

from app.automation.playwright.explorer import Explorer
from app.core.collector import Collector
from app.automation.explorer.smart_explorer import SmartExplorer
from app.automation.explorer.flow_discovery import FlowDiscovery


class Crawler:
    """
    Generic Web Application Crawler (V5)

    Responsibilities
    ----------------
    - Crawl any web application
    - Support SPA and traditional websites
    - Prevent infinite loops
    - Handle redirects safely
    - Collect exploration data

    This crawler contains NO application-specific logic.
    """

    def __init__(self, page):

        self.page = page

        self.explorer = Explorer(page)
        self.smart_explorer = SmartExplorer(page)
        self.flow_discovery = FlowDiscovery()

        parsed = urlparse(page.url)

        self.base_domain = parsed.netloc
        self.base_scheme = parsed.scheme

        self.default_max_depth = 5

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
            ".rar",
            ".7z",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".webm"

        }

        self.authentication_patterns = [

            "/login",
            "/signin",
            "/sign-in",
            "/auth",
            "/authenticate",
            "/authentication",
            "/session"

        ]

        # Already crawled URLs
        self.visited_urls = set()

        # Canonical fingerprints
        self.visited_fingerprints = set()

        # URLs waiting inside queue
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

            self.get_url_fingerprint(
                start_url
            )

        )

        page_counter = 0

        while queue:

            item = queue.popleft()

            requested_url = item["url"]
            depth = item["depth"]

            if depth > max_depth:
                continue

            requested_fp = self.get_url_fingerprint(
                requested_url
            )

            self.queued_fingerprints.discard(
                requested_fp
            )

            if requested_fp in self.visited_fingerprints:
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

                final_fp = self.get_url_fingerprint(
                    final_url
                )

                if final_fp in self.visited_fingerprints:
                    continue

                if final_url in self.visited_urls:
                    continue

                redirect_info = self.detect_redirect(
                    requested_url,
                    final_url
                )

                page_data = self.explorer.explore()
                ai_page = self.smart_explorer.analyze_page()

                current_page = ai_page["url"]

                # Add current page node
                self.flow_discovery.add_node(
                    current_page,
                    title=ai_page.get("title", ""),
                    page_type=ai_page.get("page_type", "unknown"),
                    metadata=ai_page
                )

                # Save page actions
                self.flow_discovery.set_actions(
                    current_page,
                    ai_page.get("actions", [])
                )


                for action in ai_page.get("actions", []):
                    print("=" * 60)
                    print(action)

                    target_page = action.get("target")

                    if not target_page:
                       continue

                    target_page = self.normalize_url(target_page)

                    if not target_page:
                        continue
                    print("RAW TARGET:", target_page)

                    target_page = self.normalize_url(target_page)

                    print("NORMALIZED TARGET:", target_page)

                    self.flow_discovery.add_edge(
                    current_page,
                    target_page,
                    action=action.get("action", "navigate"),
                    element=action.get("metadata", {}).get("text", ""),
                    locator=action.get("locator", "")
                    )
                       
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
                    final_fp
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

                    normalized = self.normalize_url(link)

                    if not normalized:
                        continue

                    # Don't revisit the current page
                    if normalized == final_url:
                        continue

                    # Already explored by URL
                    if normalized in self.visited_urls:
                        continue

                    # Canonical fingerprint
                    link_fp = self.get_url_fingerprint(
                        normalized
                    )

                    # Already explored
                    if link_fp in self.visited_fingerprints:
                        continue

                    # Already queued
                    if link_fp in self.queued_fingerprints:
                        continue

                    queue.append({
                        "url": normalized,
                        "depth": depth + 1
                    })

                    self.queued_fingerprints.add(
                        link_fp
                    )

                print(
                    f"QUEUE SIZE: {len(queue)}"
                )

                if (
                    max_pages
                    and len(self.visited_urls) >= max_pages
                ):
                    break

            except Exception as ex:

                print(
                    f"ERROR crawling {requested_url}: {ex}"
                )

                collector.add_error(ex)

        print("\n==============================")
        print(
            f"Total pages crawled: {len(self.visited_urls)}"
        )
        print("==============================")

        print("=" * 60)
        print("FLOW NODES:", len(self.flow_discovery.nodes))
        print("FLOW EDGES:", len(self.flow_discovery.edges))
        print("=" * 60)

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

        lower = final_url.lower()

        for pattern in self.authentication_patterns:

            if pattern in lower:

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

            # Remove duplicate slashes
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

            normalized = (
                f"{self.base_scheme}://"
                f"{parsed.netloc}"
                f"{path}"
            )

            return normalized

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
        Convert dynamic URLs into canonical fingerprints.

        Examples

        /users/7
        /users/15
            -> /users/{id}

        /orders/125/items
        /orders/300/items
            -> /orders/{id}/items
        """

        if not url:
            return None

        parsed = urlparse(url)

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

        # Replace common dynamic key/value URL patterns
        dynamic_patterns = [

            r"empnumber/\d+",
            r"candidateid/\d+",
            r"vacancyid/\d+",
            r"userid/\d+",
            r"jobid/\d+",
            r"recordid/\d+",
            r"customerid/\d+",
            r"employeeid/\d+",
            r"projectid/\d+",
            r"invoiceid/\d+",
            r"orderid/\d+",
            r"productid/\d+",
            r"companyid/\d+",
            r"departmentid/\d+",
            r"id/\d+"

        ]

        for pattern in dynamic_patterns:

            path = re.sub(

                pattern,

                lambda m: m.group(0).split("/")[0] + "/{id}",

                path,

                flags=re.IGNORECASE

            )

        return f"{parsed.netloc}{path}"
           