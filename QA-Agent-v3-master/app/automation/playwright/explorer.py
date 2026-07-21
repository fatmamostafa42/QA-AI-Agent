from urllib.parse import urlparse

from playwright.sync_api import TimeoutError

from app.scanners.element_scanner import ElementScanner
from app.scanners.form_scanner import FormScanner
from app.scanners.table_scanner import TableScanner
from app.scanners.accessibility_scanner import AccessibilityScanner
from app.scanners.page_scanner import PageScanner
from app.scanners.heading_scanner import HeadingScanner
from app.scanners.validation_scanner import ValidationScanner
from app.scanners.dialog_scanner import DialogScanner
from app.scanners.navigation_scanner import NavigationScanner
from app.scanners.component_scanner import ComponentScanner


class Explorer:
    """
    Generic Web Application Explorer

    Responsibilities
    ----------------
    - Coordinate all scanners
    - Wait until page becomes stable
    - Aggregate page knowledge
    - Normalize exploration output

    Does NOT
    ----------
    - Generate scenarios
    - Generate test cases
    - Execute business actions
    """


    def __init__(self, page):

        self.page = page

        parsed = urlparse(page.url)

        self.base_url = f"{parsed.scheme}://{parsed.netloc}"

        self.scanners = {

            "page": PageScanner(page),

            "navigation": NavigationScanner(page),

            "element": ElementScanner(page),

            "form": FormScanner(page),

            "table": TableScanner(page),

            "heading": HeadingScanner(page),

            "validation": ValidationScanner(page),

            "dialog": DialogScanner(page),

            "component": ComponentScanner(page),

            "accessibility": AccessibilityScanner(page)

        }


    # ===================================================
    # PAGE READY
    # ===================================================

    def wait_until_ready(self):

        """
        Generic waiting strategy.

        Works for:
        - React
        - Angular
        - Vue
        - Laravel
        - Django
        - ASP.NET
        - Static HTML

        Never blocks forever.
        """

        try:

            self.page.wait_for_load_state(
                "domcontentloaded",
                timeout=5000
            )

        except TimeoutError:

            pass

        except Exception:

            pass

        try:

            self.page.wait_for_load_state(
                "networkidle",
                timeout=1000
            )

        except TimeoutError:

            pass

        except Exception:

            pass

        # Small rendering delay only

        try:

            self.page.wait_for_timeout(150)

        except Exception:

            pass


    # ===================================================
    # SAFE SCANNER EXECUTION
    # ===================================================

    def run_scanner(
        self,
        scanner_name
    ):

        scanner = self.scanners.get(scanner_name)

        if scanner is None:

            return {}

        try:

            result = scanner.scan()

            if result is None:

                return {}

            return result

        except Exception as ex:

            print(
                f"{scanner_name} scanner failed: {ex}"
            )

            return {}
            # ===================================================
    # MAIN EXPLORATION
    # ===================================================

    def explore(self):

        print(
            f"\nExploring: {self.page.url}"
        )

        # ---------------------------------
        # Run lightweight scanners first
        # ---------------------------------

        page_info = self.run_scanner(
            "page"
        )

        navigation = self.run_scanner(
            "navigation"
        )

        elements = self.run_scanner(
            "element"
        )

        forms = self.run_scanner(
            "form"
        )

        tables = self.run_scanner(
            "table"
        )

        headings = self.run_scanner(
            "heading"
        )

        dialogs = self.run_scanner(
            "dialog"
        )

        validations = self.run_scanner(
            "validation"
        )

        components = self.run_scanner(
            "component"
        )

        accessibility = self.run_scanner(
            "accessibility"
        )



        # ---------------------------------
        # Safety
        # ---------------------------------

        if not isinstance(elements, dict):
            elements = {}

        if not isinstance(navigation, dict):
            navigation = {}

        if not isinstance(forms, dict):
            forms = {}

        if not isinstance(tables, dict):
            tables = {}



        # ---------------------------------
        # Metadata
        # ---------------------------------

        page_metadata = {

            "url": self.page.url,

            "title": self.safe_title(),

            "page_type": self.detect_page_type(

                elements,

                forms,

                tables

            ),

            "technology": self.detect_technology()

        }



        if isinstance(page_info, dict):

            page_metadata.update(
                page_info
            )



        # ---------------------------------
        # Final Result
        # ---------------------------------

        return {

            "page":

                page_metadata,



            "navigation": {

                "internal_links":

                    navigation.get(
                        "internal_links",
                        []
                    ),

                "external_links":

                    navigation.get(
                        "external_links",
                        []
                    ),

                "menus":

                    navigation.get(
                        "menus",
                        []
                    )

            },



            "elements": {

                "buttons":

                    elements.get(
                        "buttons",
                        []
                    ),

                "inputs":

                    elements.get(
                        "inputs",
                        []
                    ),

                "links":

                    elements.get(
                        "links",
                        []
                    ),

                "selects":

                    elements.get(
                        "selects",
                        []
                    ),

                "textareas":

                    elements.get(
                        "textareas",
                        []
                    ),

                "checkboxes":

                    elements.get(
                        "checkboxes",
                        []
                    ),

                "radio_buttons":

                    elements.get(
                        "radio_buttons",
                        []
                    )

            },



            "forms":

                forms,



            "tables":

                tables,



            "headings":

                headings,



            "dialogs":

                dialogs,



            "validations":

                validations,



            "components":

                components,



            "accessibility":

                accessibility

        }
        # ===================================
    # Generic Page Classification
    # ===================================

    def detect_page_type(
        self,
        elements,
        forms,
        tables
    ):

        url = self.page.url.lower()

        try:
            title = self.page.title().lower()
        except Exception:
            title = ""

        inputs = elements.get("inputs", [])
        buttons = elements.get("buttons", [])

        # Login

        if (
            "login" in url
            or "signin" in url
            or "password" in str(inputs).lower()
        ):
            return "login"

        # Dashboard

        if (
            "dashboard" in url
            or "dashboard" in title
        ):
            return "dashboard"

        # List Page

        if tables:
            return "list"

        # Form

        if len(inputs) > 0 and len(buttons) > 0:
            return "form"

        # Details

        if (
            "details" in url
            or "view" in url
        ):
            return "details"

        return "unknown"



    # ===================================
    # Technology Detection
    # ===================================

    def detect_technology(self):

        technologies = []

        try:

              html = self.safe_content().lower()

        except Exception:

            return ["unknown"]

        signatures = {

            "Angular": [
                "ng-version",
                "ng-app"
            ],

            "React": [
                "__react",
                "reactroot",
                "_reactroot"
            ],

            "Vue": [
                "__vue__",
                "vue.js",
                "vuex"
            ],

            "Bootstrap": [
                "bootstrap",
                "btn btn-",
                "container-fluid"
            ],

            "Tailwind": [
                "tailwind",
                "tw-"
            ]

        }

        for tech, patterns in signatures.items():

            for pattern in patterns:

                if pattern in html:

                    technologies.append(tech)
                    break

        if not technologies:

            technologies.append("unknown")

        return technologies
        # ===================================
    # Safe Helpers
    # ===================================

    def safe_title(self):
        """
        Safely return page title.
        """

        try:
            return self.page.title().strip()
        except Exception:
            return ""


    def safe_content(self):
        """
        Safely return page HTML.
        """

        try:
            return self.page.content()
        except Exception:
            return ""


    def safe_url(self):
        """
        Safely return current URL.
        """

        try:
            return self.page.url
        except Exception:
            return ""