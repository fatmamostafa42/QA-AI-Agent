from collections import deque
from urllib.parse import urlparse, urljoin
import re

from app.automation.playwright.explorer import Explorer
from app.core.collector import Collector
from app.automation.explorer.smart_explorer import SmartExplorer
from app.automation.explorer.flow_discovery import FlowDiscovery
from app.automation.explorer.execution_engine import ExecutionEngine


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
        self.execution_engine = ExecutionEngine(self.page)

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
        self.executed_actions = set()
        self.failed_actions = set()
        self.queued_actions = set()
        self.stats = {
            "actions_discovered": 0,
            "actions_executed": 0,
            "pages_visited": 0
        }
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

            "type": "url",
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
            print(f"POP -> {item['type']} : {item.get('url')}")
            item_type = item["type"]

            depth = item["depth"]

            if item_type == "url":

                requested_url = item["url"]

            elif item_type == "action":

                action = item["action"]
                

            else:
                continue
            if depth > max_depth:
                continue


            if item_type == "url":

                requested_fp = self.get_url_fingerprint(
                    requested_url
                )

                self.queued_fingerprints.discard(
                    requested_fp
                )

                if requested_fp in self.visited_fingerprints:
                    print("SKIP: visited fingerprint")
                    continue

            elif item_type == "action":

                action_id = self.get_action_fingerprint(
                    action
                )
                self.queued_actions.discard(action_id)
                print(
                    "QUEUE ACTION:",
                    action.get("locator"),
                    action_id
                )

                if action_id in self.executed_actions:
                    print("SKIP: executed action")
                    continue
                

            page_counter += 1

            print(
                f"\n[{page_counter}] Visiting: {requested_url}"
            )

            print(
                f"Depth: {depth}"
            )

            try:
                result = None
                if item_type == "url":

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

                elif item_type == "action":
                    source_url = action.get("source_url") or item["url"]

                    if self.normalize_url(self.page.url) != self.normalize_url(source_url):

                        print(f"RETURN TO SOURCE: {source_url}")

                        self.page.goto(
                            source_url,
                            wait_until="domcontentloaded",
                            timeout=30000
                        )


                    self.explorer.wait_until_ready()

                  
                    print(
                        f"EXECUTING ACTION: {action.get('locator')}"
                    )

                    result = self.execution_engine.execute(action)

                    print("=" * 60)
                    print("CURRENT PAGE :", self.page.url)
                    print("SOURCE PAGE  :", source_url)
                    print("ACTION       :", action.get("locator"))
                    print("=" * 60)
                    print(
                        "EXECUTING ACTION:",
                        action.get("action"),
                        action.get("locator")
                    )


                    print(result)

                    action_fp = self.get_action_fingerprint(action)

                    if result and result.get("success"):
                        self.executed_actions.add(action_fp)
                        self.stats["actions_executed"] += 1
                    else:
                        self.failed_actions.add(action_fp)

                    self.explorer.wait_until_ready()

                    final_url = self.normalize_url(
                        self.page.url
                    )

                    if not final_url:
                        continue
                   

                    final_fp = self.get_url_fingerprint(
                        final_url
                    )

                    redirect_info = {
                    "redirected": False,
                    "redirect_reason": None
                    }

                    requested_url = final_url

                page_data = self.explorer.explore()

                ai_page = self.smart_explorer.analyze_page()

                actions = ai_page.get("actions", [])

                queued_count = 0

                
                for action in actions:

                    if action["action"] not in ("navigate", "click"):
                        continue

                    locator = action.get("locator", {})

                    if locator.get("value") == "unknown":
                        continue

                    target = action.get("target")
                    metadata = action.get("metadata", {})
                    navigation = metadata.get("navigation", {})
                    attributes = metadata.get("attributes", "")

                    is_navigable = (
                        target not in ("", None, "#")
                        or action.get("may_navigate")
                        or navigation.get("detected")
                        or metadata.get("tag") == "button"
                        or "role=tab" in attributes
                        or "role=menuitem" in attributes
                    )

                    if not is_navigable:
                        continue

                    action_fp = self.get_action_fingerprint(action)

                    if action_fp in self.executed_actions:
                        continue

                    if action_fp in self.failed_actions:
                        continue

                    if action_fp in self.queued_actions:
                        continue

                    self.queued_actions.add(action_fp)
                    queued_count += 1

                    action["source_url"] = final_url

                    queue.append({

                        "type": "action",
                        "action": action,
                        "url": final_url,
                        "depth": depth + 1

                    })
                self.stats["actions_discovered"] += queued_count

                print(
                    f"NEW ACTIONS QUEUED: {queued_count} | "
                    f"QUEUE SIZE: {len(queue)}"
                )   

                new_page_data = page_data

                new_ai_page = ai_page             

                current_page = new_ai_page["url"]

                if (
                    result
                    and result["success"]
                    and result["navigated"]
                ):   
                    print("=" * 60)
                    print("EDGE DEBUG")
                    print("ACTION :", action.get("action"))
                    print("TEXT   :", action.get("metadata", {}).get("text"))
                    print("LOCATOR:", action.get("locator"))
                    print("=" * 60) 

                    self.flow_discovery.add_edge(
                        result["old_state"]["url"],
                        result["new_state"]["url"],
                        action=result["action"],
                        element=action.get("metadata", {}).get("text", ""),
                        locator=action.get("locator", {})
                    )

                    print(
                        f"ADD EDGE: "
                        f'{result["old_state"]["url"]} ---> '
                        f'{result["new_state"]["url"]}'
                    )

                # Add current page node
                self.flow_discovery.add_node(
                    current_page,
                    title=new_ai_page.get("title", ""),
                    page_type=new_ai_page.get("page_type", "unknown"),
                    metadata=new_ai_page
                )

                # Save page actions
                self.flow_discovery.set_actions(
                    current_page,
                    new_ai_page.get("actions", [])
                )
                     
                new_page_data["page"]["requested_url"] = requested_url
                new_page_data["page"]["final_url"] = final_url
                new_page_data["page"]["crawl_depth"] = depth
                new_page_data["page"].update(
                    redirect_info
                )

                collector.add_page(
                    new_page_data
                )
               
                visited_url = final_url

                visited_fp = final_fp

                self.visited_urls.add(
                visited_url
                )
                self.stats["pages_visited"] += 1

                self.visited_fingerprints.add(
                visited_fp
                )

                if redirect_info.get(
                    "redirect_reason"
                ) == "authentication_required":

                    print(
                        "Authentication page detected - skipping children"
                    )

                    continue


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
      
        print("\n========== CRAWL SUMMARY ==========")
        print("Pages Visited:", len(self.visited_urls))
        print("Actions Discovered:", self.stats["actions_discovered"])
        print("Actions Executed:", self.stats["actions_executed"])
        print("Queued Actions Left:", len(self.queued_actions))
        print("Flow Nodes:", len(self.flow_discovery.nodes))
        print("Flow Edges:", len(self.flow_discovery.edges))
        print("===================================")

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
    
    def get_action_fingerprint(self, action):

        locator = action.get("locator", {})
        metadata = action.get("metadata", {})
        navigation = metadata.get("navigation", {})

        target = (
            navigation.get("target")
            or action.get("target")
            or ""
        )

        return (
            action.get("action"),
            locator.get("strategy"),
            locator.get("value"),
            target,
            metadata.get("tag"),
        )