class PageScanner:

    def __init__(self, page):
        self.page = page

    def scan(self):

        return {

            "url": self.page.url,

            "title": self.page.title(),

            "viewport": self.page.viewport_size,

            "has_horizontal_scroll": self.page.evaluate(
                """
                () => document.body.scrollWidth >
                      window.innerWidth
                """
            ),

            "language": self.page.locator("html").get_attribute("lang"),

            "page_text": self.page.locator("body").inner_text()[:10000]

        }