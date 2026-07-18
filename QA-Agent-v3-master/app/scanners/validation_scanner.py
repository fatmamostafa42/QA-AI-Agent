class ValidationScanner:

    def __init__(self, page):
        self.page = page

    def scan(self):

        validations = []

        for field in self.page.locator(
            "input, textarea, select"
        ).all():

            try:

                validations.append({

                    "required":
                        field.get_attribute("required") is not None,

                    "type":
                        field.get_attribute("type"),

                    "maxlength":
                        field.get_attribute("maxlength"),

                    "minlength":
                        field.get_attribute("minlength"),

                    "pattern":
                        field.get_attribute("pattern"),

                    "placeholder":
                        field.get_attribute("placeholder")

                })

            except Exception:
                pass

        return validations