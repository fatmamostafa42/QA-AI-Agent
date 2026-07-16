from urllib.parse import urlparse

from app.scanners.element_scanner import ElementScanner
from app.scanners.form_scanner import FormScanner
from app.scanners.table_scanner import TableScanner


class Explorer:
    """
    Coordinates all scanners.
    Explorer does not scan DOM directly.
    It only collects results from scanners.
    """

    def __init__(self, page):

        print("EXPLORER LOADED")

        self.page = page

        parsed = urlparse(page.url)

        self.base_url = f"{parsed.scheme}://{parsed.netloc}"

        self.element_scanner = ElementScanner(page)
        self.form_scanner = FormScanner(page)
        self.table_scanner = TableScanner(page)


    def wait_until_ready(self):

        print("WAITING FOR PAGE READY...")


        # 1- Wait until HTML is loaded
        try:

            self.page.wait_for_load_state(
                "domcontentloaded"
            )

            print(
                "DOM CONTENT LOADED"
            )

        except Exception as e:

            print(
                f"DOM LOAD WARNING: {e}"
            )


        # 2- Wait for network requests to settle
        try:

            self.page.wait_for_load_state(
                "networkidle",
                timeout=10000
            )

            print(
                "NETWORK IDLE REACHED"
            )


        except Exception:

            print(
                "Network idle timeout, continue..."
            )


        # 3- Wait for SPA rendering (React/Vue/Angular)
        self.page.wait_for_timeout(
            3000
        )


        print(
            "SPA RENDERING WAIT COMPLETED"
        )



    def explore(self):

        print(
            "START EXPLORING PAGE:"
        )

        print(
            self.page.url
        )


        buttons = self.element_scanner.buttons()

        print(
            f"BUTTONS FOUND: {len(buttons)}"
        )


        inputs = self.element_scanner.inputs()

        print(
            f"INPUTS FOUND: {len(inputs)}"
        )


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

            },


            "forms":

                self.form_scanner.scan(),


            "tables":

                self.table_scanner.scan(),

        }