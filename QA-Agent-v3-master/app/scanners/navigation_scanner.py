class NavigationScanner:

    def __init__(self, page):

        self.page = page

    def scan(self):

        menus = []

        try:

            links = self.page.locator("nav a")

            count = links.count()

            for i in range(count):

                try:

                    text = links.nth(i).inner_text().strip()

                    href = links.nth(i).get_attribute("href")

                    if text:

                        menus.append({

                            "text": text,

                            "href": href

                        })

                except Exception:
                    pass

        except Exception:
            pass

        return menus