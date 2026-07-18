class HeadingScanner:

    def __init__(self, page):
        self.page = page

    def scan(self):

        headings = []

        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:

            for h in self.page.locator(tag).all():

                try:

                    text = h.inner_text().strip()

                    if text:

                        headings.append({

                            "tag": tag,

                            "text": text

                        })

                except Exception:
                    pass

        return headings