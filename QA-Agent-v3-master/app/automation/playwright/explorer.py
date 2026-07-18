from urllib.parse import urlparse

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
    Coordinates all scanners.

    Explorer never scans the DOM directly.
    Each scanner has a single responsibility.
    """


    def __init__(self, page):

        self.page = page

        parsed = urlparse(page.url)

        self.base_url = (
            f"{parsed.scheme}://{parsed.netloc}"
        )


        # -----------------------------
        # Core scanners
        # -----------------------------

        self.element_scanner = ElementScanner(page)

        self.form_scanner = FormScanner(page)

        self.table_scanner = TableScanner(page)

        self.accessibility_scanner = AccessibilityScanner(page)



        # -----------------------------
        # Smart scanners
        # -----------------------------

        self.page_scanner = PageScanner(page)

        self.heading_scanner = HeadingScanner(page)

        self.validation_scanner = ValidationScanner(page)

        self.dialog_scanner = DialogScanner(page)

        self.navigation_scanner = NavigationScanner(page)



        # -----------------------------
        # Modern UI Components
        # React / Angular / Vue / SPA
        # -----------------------------

        self.component_scanner = ComponentScanner(page)



    def wait_until_ready(self):

        try:

            self.page.wait_for_load_state(
                "domcontentloaded"
            )

        except Exception:

            pass



        try:

            self.page.wait_for_load_state(
                "networkidle",
                timeout=10000
            )

        except Exception:

            pass



        self.page.wait_for_timeout(3000)



    def explore(self):

        print(
            f"\nExploring: {self.page.url}"
        )



        # -----------------------------
        # Elements
        # -----------------------------

        buttons = self.element_scanner.buttons()

        inputs = self.element_scanner.inputs()

        links = self.element_scanner.links()

        selects = self.element_scanner.selects()

        textareas = self.element_scanner.textareas()



        # -----------------------------
        # Forms / Tables
        # -----------------------------

        forms = self.form_scanner.scan()

        tables = self.table_scanner.scan()



        # -----------------------------
        # Accessibility
        # -----------------------------

        accessibility = (
            self.accessibility_scanner.scan()
        )



        # -----------------------------
        # Smart Scanners
        # -----------------------------

        page_info = (
            self.page_scanner.scan()
        )


        headings = (
            self.heading_scanner.scan()
        )


        validations = (
            self.validation_scanner.scan()
        )


        dialogs = (
            self.dialog_scanner.scan()
        )


        menus = (
            self.navigation_scanner.scan()
        )



        # -----------------------------
        # Modern Components
        # -----------------------------

        components = (
            self.component_scanner.scan()
        )



        return {


            "page": {

                "url":
                    self.page.url,


                "title":
                    self.page.title(),


                **page_info

            },



            "navigation": {


                "internal_links":
                    self.element_scanner.internal_links(),



                "external_links":
                    self.element_scanner.external_links(),



                "menus":
                    menus

            },



            "elements": {


                "buttons":
                    buttons,


                "inputs":
                    inputs,


                "links":
                    links,


                "selects":
                    selects,


                "textareas":
                    textareas

            },



            "forms":
                forms,



            "tables":
                tables,



            "components":
                components,



            "headings":
                headings,



            "dialogs":
                dialogs,



            "validations":
                validations,



            "accessibility":
                accessibility

        }