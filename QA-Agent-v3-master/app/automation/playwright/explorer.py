from urllib.parse import urlparse

from app.scanners.element_scanner import ElementScanner
from app.scanners.form_scanner import FormScanner
from app.scanners.table_scanner import TableScanner
from app.scanners.accessibility_scanner import AccessibilityScanner


class Explorer:
    """
    Coordinates all scanners.

    Explorer does not scan DOM directly.
    It only coordinates all scanners and combines their results.
    """

    def __init__(self, page):

        print("EXPLORER LOADED")

        self.page = page

        parsed = urlparse(page.url)

        self.base_url = f"{parsed.scheme}://{parsed.netloc}"

        self.element_scanner = ElementScanner(page)
        self.form_scanner = FormScanner(page)
        self.table_scanner = TableScanner(page)
        self.accessibility_scanner = AccessibilityScanner(page)

    def wait_until_ready(self):

        print("WAITING FOR PAGE READY...")

        # Wait until HTML is loaded
        try:

            self.page.wait_for_load_state("domcontentloaded")

            print("DOM CONTENT LOADED")

        except Exception as e:

            print(f"DOM LOAD WARNING: {e}")

        # Wait until network requests finish
        try:

            self.page.wait_for_load_state(
                "networkidle",
                timeout=10000
            )

            print("NETWORK IDLE REACHED")

        except Exception:

            print("Network idle timeout, continue...")

        # Wait for SPA rendering
        self.page.wait_for_timeout(3000)

        print("SPA RENDERING WAIT COMPLETED")

    def explore(self):

        print("START EXPLORING PAGE:")
        print(self.page.url)

        buttons = self.element_scanner.buttons()
        print(f"BUTTONS FOUND: {len(buttons)}")

        inputs = self.element_scanner.inputs()
        print(f"INPUTS FOUND: {len(inputs)}")

        links = self.element_scanner.links()
        print(f"LINKS FOUND: {len(links)}")

        selects = self.element_scanner.selects()
        print(f"SELECTS FOUND: {len(selects)}")

        textareas = self.element_scanner.textareas()
        print(f"TEXTAREAS FOUND: {len(textareas)}")

        forms = self.form_scanner.scan()
        print(f"FORMS FOUND: {len(forms)}")

        tables = self.table_scanner.scan()
        print(f"TABLES FOUND: {len(tables)}")

        accessibility = self.accessibility_scanner.scan()
        print(f"ACCESSIBILITY ELEMENTS FOUND: {len(accessibility)}")

        return {

            "page": {

                "url": self.page.url,

                "title": self.page.title(),

            },

            "navigation": {

                "internal_links":
                    self.element_scanner.internal_links(),

                "external_links":
                    self.element_scanner.external_links(),

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
                    textareas,

            },

            "forms":
                forms,

            "tables":
                tables,

            "accessibility":
                accessibility,

        }