from playwright.sync_api import Page


class ElementScanner:
    """
    Scans common UI elements from the current page.
    """

    def __init__(self, page: Page):
        self.page = page

    def scan(self) -> dict:
        return {
            "buttons": self.buttons(),
            "inputs": self.inputs(),
            "links": self.links(),
            "selects": self.selects(),
            "textareas": self.textareas(),
        }

    def buttons(self):

        buttons = []

        locator = self.page.locator("button")

        count = locator.count()

        for i in range(count):

            try:

                button = locator.nth(i)

                text = button.inner_text().strip()

                if text:

                    buttons.append({
                        "text": text
                    })

            except Exception as e:

                print(f"Button Error: {e}")

        return buttons


    def inputs(self):

        inputs = []

        locator = self.page.locator("input")

        count = locator.count()

        for i in range(count):

            try:

                element = locator.nth(i)

                inputs.append({

                    "type": element.get_attribute("type"),
                    "name": element.get_attribute("name"),
                    "id": element.get_attribute("id"),
                    "placeholder": element.get_attribute("placeholder")

                })

            except Exception as e:

                print(f"Input Error: {e}")

        return inputs


    def links(self):

        links = []

        locator = self.page.locator("a")

        count = locator.count()

        for i in range(count):

            try:

                link = locator.nth(i)

                links.append({

                    "text": link.inner_text().strip(),
                    "href": link.get_attribute("href")

                })

            except Exception as e:

                print(f"Link Error: {e}")

        return links


    def selects(self):

        selects = []

        locator = self.page.locator("select")

        count = locator.count()

        for i in range(count):

            try:

                select = locator.nth(i)

                selects.append({

                    "name": select.get_attribute("name"),
                    "id": select.get_attribute("id")

                })

            except Exception as e:

                print(f"Select Error: {e}")

        return selects


    def textareas(self):

        textareas = []

        locator = self.page.locator("textarea")

        count = locator.count()

        for i in range(count):

            try:

                area = locator.nth(i)

                textareas.append({

                    "name": area.get_attribute("name"),
                    "id": area.get_attribute("id"),
                    "placeholder": area.get_attribute("placeholder")

                })

            except Exception as e:

                print(f"Textarea Error: {e}")

        return textareas


    def internal_links(self):

        links = []

        domain = self.page.url.split("/")[2]

        for link in self.links():

            href = link.get("href")

            if not href:
                continue

            if href.startswith("/"):

                links.append(
                    self.page.url.split(domain)[0] + domain + href
                )

            elif domain in href:

                links.append(href)

        return sorted(set(links))


    def external_links(self):

        links = []

        domain = self.page.url.split("/")[2]

        for link in self.links():

            href = link.get("href")

            if not href:
                continue

            if href.startswith("http") and domain not in href:

                links.append(href)

        return sorted(set(links))