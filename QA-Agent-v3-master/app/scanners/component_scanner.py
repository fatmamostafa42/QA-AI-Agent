from playwright.sync_api import Page

from app.scanners.locator_builder import LocatorBuilder


class ComponentScanner:
    """
    Generic Web Component Scanner.

    Framework independent:
    Supports:
    - React
    - Angular
    - Vue
    - Svelte
    - Vanilla JS
    - Server rendered applications

    Detection is based on:
    - DOM structure
    - ARIA roles
    - Common UI patterns
    """


    def __init__(self, page: Page):

        self.page = page
        self.locator_builder = LocatorBuilder(page)



    def scan(self):

        return {

            "data_grids":
                self._scan_grids(),


            "cards":
                self._scan_cards(),


            "tabs":
                self._scan_tabs(),


            "dialogs":
                self._scan_dialogs(),


            "dropdowns":
                self._scan_dropdowns(),


            "component_summary":
                self._summary()

        }



    # ==================================================
    # Data Grid Scanner
    # ==================================================

    def _scan_grids(self):

        grids = []


        selectors = [

            "[role='grid']",

            "[role='table']",

            "[role='treegrid']",


            "table",


            ".ag-root",

            ".mat-table",

            ".p-datatable",

            ".v-data-table",

            ".oxd-table"

        ]


        seen = set()


        for selector in selectors:

            try:

                elements = self.page.locator(selector)

                count = elements.count()


                for i in range(count):

                    grid = elements.nth(i)


                    locator = (
                        self.locator_builder.build(grid)
                    )


                    if locator in seen:
                        continue


                    seen.add(locator)



                    grids.append({

                        "type":
                            "data_grid",


                        "locator":
                            locator,


                        "columns":
                            self._extract_columns(grid),


                        "actions":
                            self._extract_actions(grid),


                        "features": {

                            "pagination":
                                self._has_pagination(),


                            "search":
                                self._has_search(),


                            "filters":
                                self._has_filters()

                        }

                    })


            except Exception:
                pass



        return grids





    def _extract_columns(self, grid):

        columns = []


        selectors = [

            "[role='columnheader']",

            "thead th",

            "th",

            ".header"

        ]


        for selector in selectors:

            try:

                for item in grid.locator(selector).all():

                    text = (
                        item.inner_text()
                        .strip()
                    )


                    if text:
                        columns.append(text)


            except Exception:
                pass



        return sorted(set(columns))





    def _extract_actions(self, grid):

        actions = []


        keywords = [

            "edit",
            "delete",
            "view",
            "details",
            "approve",
            "reject",
            "remove",
            "update",
            "save",
            "cancel"

        ]


        try:

            buttons = grid.locator(
                "button"
            ).all()


            for button in buttons:

                text = (
                    button.inner_text()
                    .strip()
                    .lower()
                )


                for keyword in keywords:

                    if keyword in text:

                        actions.append(
                            keyword.title()
                        )


        except Exception:

            pass



        return sorted(set(actions))





    # ==================================================
    # Card Scanner
    # ==================================================

    def _scan_cards(self):

        cards = []


        selectors = [

            ".card",

            "[class*='card']",

            "[class*='widget']",

            "[role='region']"

        ]


        seen = set()



        for selector in selectors:

            try:

                elements = self.page.locator(selector)


                for i in range(
                    elements.count()
                ):

                    card = elements.nth(i)


                    text = (
                        card.inner_text()
                        .strip()
                    )


                    if not text:
                        continue



                    key = text[:100]


                    if key in seen:
                        continue


                    seen.add(key)



                    lines = [
                        x.strip()
                        for x in text.split("\n")
                        if x.strip()
                    ]



                    cards.append({

                        "type":
                            "card",


                        "selector":
                            selector,


                        "title":
                            lines[0]
                            if lines
                            else "",


                        "content":
                            lines[:5],


                        "locator":
                            self.locator_builder.build(card)

                    })


            except Exception:

                pass



        return cards





    # ==================================================
    # Tabs
    # ==================================================

    def _scan_tabs(self):

        tabs = []


        selectors = [

            "[role='tab']",

            ".tab",

            ".tabs button"

        ]


        for selector in selectors:


            try:

                for tab in self.page.locator(selector).all():

                    text = (
                        tab.inner_text()
                        .strip()
                    )


                    if text:

                        tabs.append(text)


            except Exception:

                pass



        return sorted(set(tabs))





    # ==================================================
    # Dialog / Modal
    # ==================================================

    def _scan_dialogs(self):

        dialogs = []


        selectors = [

            "[role='dialog']",

            ".modal",

            ".dialog"

        ]



        for selector in selectors:


            try:

                for dialog in self.page.locator(selector).all():


                    text = (
                        dialog.inner_text()
                        .strip()
                    )


                    dialogs.append({

                        "type":
                            "dialog",


                        "title":
                            text.split("\n")[0]
                            if text
                            else "",


                        "text":
                            text[:300],


                        "buttons":
                            self._dialog_buttons(dialog),


                        "inputs":
                            dialog.locator(
                                "input,textarea,select"
                            ).count()

                    })


            except Exception:

                pass



        return dialogs





    def _dialog_buttons(self, dialog):

        buttons = []


        try:

            for button in dialog.locator(
                "button"
            ).all():


                text = (
                    button.inner_text()
                    .strip()
                )


                if text:

                    buttons.append(text)


        except Exception:

            pass


        return buttons





    # ==================================================
    # Dropdowns
    # ==================================================

    def _scan_dropdowns(self):

        return {


            "native_selects":
                self.page.locator(
                    "select"
                ).count(),



            "aria_combobox":
                self.page.locator(
                    "[role='combobox']"
                ).count(),



            "custom_dropdowns":
                self.page.locator(
                    "[aria-haspopup='listbox']"
                ).count()

        }




    # ==================================================
    # Helpers
    # ==================================================

    def _has_pagination(self):

        selectors = [

            ".pagination",

            "[aria-label*='pagination']",

            ".oxd-pagination",

            ".mat-paginator"

        ]


        return any(

            self.page.locator(s).count()
            > 0

            for s in selectors

        )



    def _has_search(self):

        selectors = [

            "input[type='search']",


            "input[placeholder*='Search']"


        ]


        return any(

            self.page.locator(s).count()
            > 0

            for s in selectors

        )



    def _has_filters(self):

        return (

            self.page.locator(
                "select"
            ).count()

            +

            self.page.locator(
                "input[type='checkbox']"
            ).count()

            +

            self.page.locator(
                "input[type='date']"
            ).count()

        ) > 0




    def _summary(self):

        return {

            "framework_independent":
                True,


            "supported_patterns":[

                "ARIA",

                "HTML",

                "CSS patterns",

                "UI libraries"

            ]

        }