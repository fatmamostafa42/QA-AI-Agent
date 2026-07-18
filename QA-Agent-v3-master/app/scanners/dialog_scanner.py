class DialogScanner:

    def __init__(self, page):
        self.page = page

    def scan(self):

        dialogs = []

        selectors = [

            "[role='dialog']",
            ".modal",
            ".popup",
            ".toast",
            ".alert",
            ".notification"

        ]

        for selector in selectors:

            try:

                for dialog in self.page.locator(selector).all():

                    text = dialog.inner_text().strip()

                    if text:

                        dialogs.append({

                            "type": selector,

                            "text": text

                        })

            except Exception:
                pass

        return dialogs