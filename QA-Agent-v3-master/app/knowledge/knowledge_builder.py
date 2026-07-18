from typing import Dict, List


class KnowledgeBuilder:
    """
    Converts Exploration JSON into structured Knowledge.

    Explorer
        ↓
    Knowledge Builder
        ↓
    Requirement Analyzer
        ↓
    Feature Splitter
        ↓
    Scenario Generator
    """

    def __init__(self, exploration: Dict):

        self.exploration = exploration

    def build(self) -> Dict:

        pages = self.exploration.get("pages", [])

        return {

            "application": self._application(),

            "summary": self._summary(pages),

            "pages": [

                self._page(page)

                for page in pages

            ]

        }

    def _application(self):

        return self.exploration.get(
            "application",
            {}
        )

    def _summary(self, pages):

        summary = {

            "pages": len(pages),

            "buttons": 0,

            "inputs": 0,

            "links": 0,

            "forms": 0,

            "tables": 0,

            "dialogs": 0,

            "menus": 0,

            "headings": 0,

            "validation_messages": 0,

            "accessibility_items": 0

        }

        for page in pages:

            elements = page.get("elements", {})

            summary["buttons"] += len(
                elements.get("buttons", [])
            )

            summary["inputs"] += len(
                elements.get("inputs", [])
            )

            summary["links"] += len(
                elements.get("links", [])
            )

            summary["forms"] += len(
                page.get("forms", [])
            )

            summary["tables"] += len(
                page.get("tables", [])
            )

            summary["dialogs"] += len(
                page.get("dialogs", [])
            )

            summary["menus"] += len(
                page.get("navigation", {}).get("menus", [])
            )

            summary["headings"] += len(
                page.get("headings", [])
            )

            summary["validation_messages"] += len(
                page.get("validations", [])
            )

            summary["accessibility_items"] += len(
                page.get("accessibility", [])
            )

        return summary

    def _page(self, page):

        elements = page.get("elements", {})

        buttons = elements.get("buttons", [])

        inputs = elements.get("inputs", [])

        links = elements.get("links", [])

        forms = page.get("forms", [])

        headings = page.get("headings", [])

        dialogs = page.get("dialogs", [])

        validations = page.get("validations", [])

        menus = page.get(
            "navigation",
            {}
        ).get(
            "menus",
            []
        )

        return {

            # --------------------------------

            # Basic

            # --------------------------------

            "url":

                page.get("page", {}).get("url"),

            "title":

                page.get("page", {}).get("title"),

            "page_type":

                page.get("page", {}).get("page_type", ""),

            "description":

                page.get("page", {}).get("description", ""),

            "breadcrumbs":

                page.get("page", {}).get("breadcrumbs", []),

            # --------------------------------

            # Counts

            # --------------------------------

            "buttons":

                len(buttons),

            "inputs":

                len(inputs),

            "links":

                len(links),

            "selects":

                len(elements.get("selects", [])),

            "textareas":

                len(elements.get("textareas", [])),

            "forms":

                len(forms),

            "tables":

                len(page.get("tables", [])),

            "dialogs":

                len(dialogs),

            "headings":

                len(headings),

            "menus":

                len(menus),

            "validation_messages":

                len(validations),

            "accessibility":

                len(page.get("accessibility", [])),

            # --------------------------------

            # Smart Knowledge

            # --------------------------------

            "button_texts":

                sorted({

                    b.get("text", "").strip()

                    for b in buttons

                    if b.get("text", "").strip()

                }),

            "input_placeholders":

                sorted({

                    i.get("placeholder", "").strip()

                    for i in inputs

                    if i.get("placeholder")

                }),

            "input_names":

                sorted({

                    i.get("name", "").strip()

                    for i in inputs

                    if i.get("name")

                }),

            "form_fields":

                sorted({

                    value.strip()

                    for form in forms

                    for field in form.get("fields", [])

                    for value in [

                        field.get("placeholder"),

                        field.get("label"),

                        field.get("name"),

                        field.get("id")

                    ]

                    if value and value.strip()

                }),

            "navigation":

                sorted({

                    l.get("text", "").strip()

                    for l in links

                    if l.get("text", "").strip()

                }),

            "menu_items":

                sorted({

                    m.get("text", "").strip()

                    for m in menus

                    if m.get("text", "").strip()

                }),

            "headings_text":

                sorted({

                    h.get("text", "").strip()

                    for h in headings

                    if h.get("text", "").strip()

                }),

            "dialog_titles":

                sorted({

                    d.get("title", "").strip()

                    for d in dialogs

                    if d.get("title", "").strip()

                }),

            "validation_texts":

                sorted({

                    v.get("text", "").strip()

                    for v in validations

                    if v.get("text", "").strip()

                })

        }