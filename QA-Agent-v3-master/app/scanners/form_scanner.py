from playwright.sync_api import Page

from app.scanners.locator_builder import LocatorBuilder


class FormScanner:
    """
    Scans all forms الموجودة في الصفحة مع جميع الحقول الخاصة بها.
    """

    def __init__(self, page: Page):
        self.page = page
        self.locator_builder = LocatorBuilder(page)

    def scan(self):

        forms = []

        for form in self.page.locator("form").all():

            forms.append({
                "action": form.get_attribute("action"),
                "method": (form.get_attribute("method") or "GET").upper(),
                "id": form.get_attribute("id"),
                "name": form.get_attribute("name"),
                "locator": self.locator_builder.build(form),
                "fields": self._scan_fields(form),
                "submit_buttons": self._scan_submit_buttons(form),
            })

        return forms

    def _scan_fields(self, form):

        fields = []

        for field in form.locator("input, textarea, select").all():

            fields.append({
                "tag": field.evaluate("el => el.tagName.toLowerCase()"),
                "type": field.get_attribute("type"),
                "name": field.get_attribute("name"),
                "id": field.get_attribute("id"),
                "placeholder": field.get_attribute("placeholder"),
                "required": field.get_attribute("required") is not None,
                "disabled": field.get_attribute("disabled") is not None,
                "readonly": field.get_attribute("readonly") is not None,
                "locator": self.locator_builder.build(field),
            })

        return fields

    def _scan_submit_buttons(self, form):

        buttons = []

        elements = form.locator(
            "button, input[type='submit'], input[type='button']"
        ).all()

        for button in elements:

            text = button.inner_text().strip()

            if not text:
                text = (
                    button.get_attribute("value")
                    or button.get_attribute("aria-label")
                    or ""
                )

            buttons.append({
                "text": text,
                "type": button.get_attribute("type"),
                "locator": self.locator_builder.build(button),
            })

        return buttons