from typing import Dict


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

        pages = self.exploration.get(
            "pages",
            []
        )


        return {

            "application":
                self._application(),


            "summary":
                self._summary(pages),


            "pages":[

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

            "buttons":0,

            "inputs":0,

            "links":0,

            "forms":0,

            "tables":0,

            "dialogs":0,

            "components":0,

            "cards":0,

            "grids":0,

            "menus":0,

            "headings":0,

            "validation_messages":0,

            "accessibility_items":0

        }



        for page in pages:


            elements = page.get(
                "elements",
                {}
            )


            components = page.get(
                "components",
                {}
            )


            summary["buttons"] += len(
                elements.get(
                    "buttons",
                    []
                )
            )


            summary["inputs"] += len(
                elements.get(
                    "inputs",
                    []
                )
            )


            summary["links"] += len(
                elements.get(
                    "links",
                    []
                )
            )


            summary["forms"] += len(
                page.get(
                    "forms",
                    []
                )
            )


            summary["tables"] += len(
                page.get(
                    "tables",
                    []
                )
            )


            summary["dialogs"] += len(
                page.get(
                    "dialogs",
                    []
                )
            )


            summary["menus"] += len(
                page.get(
                    "navigation",
                    {}
                ).get(
                    "menus",
                    []
                )
            )


            summary["headings"] += len(
                page.get(
                    "headings",
                    []
                )
            )


            summary["validation_messages"] += len(
                page.get(
                    "validations",
                    []
                )
            )


            summary["accessibility_items"] += len(
                page.get(
                    "accessibility",
                    []
                )
            )



            summary["cards"] += len(
                components.get(
                    "cards",
                    []
                )
            )


            summary["grids"] += len(
                components.get(
                    "data_grids",
                    []
                )
            )


            summary["components"] += (

                len(
                    components.get(
                        "cards",
                        []
                    )
                )

                +

                len(
                    components.get(
                        "data_grids",
                        []
                    )
                )

                +

                len(
                    components.get(
                        "dialogs",
                        []
                    )
                )

            )



        return summary






    def _page(self,page):


        elements = page.get(
            "elements",
            {}
        )


        buttons = elements.get(
            "buttons",
            []
        )


        inputs = elements.get(
            "inputs",
            []
        )


        links = elements.get(
            "links",
            []
        )


        forms = page.get(
            "forms",
            []
        )


        headings = page.get(
            "headings",
            []
        )


        dialogs = page.get(
            "dialogs",
            []
        )


        validations = page.get(
            "validations",
            []
        )


        menus = page.get(
            "navigation",
            {}
        ).get(
            "menus",
            []
        )


        components = page.get(
            "components",
            {}
        )



        cards = components.get(
            "cards",
            []
        )


        grids = components.get(
            "data_grids",
            []
        )



        return {


            "url":

                page.get(
                    "page",
                    {}
                ).get(
                    "url"
                ),



            "title":

                page.get(
                    "page",
                    {}
                ).get(
                    "title"
                ),



            "page_type":

                page.get(
                    "page",
                    {}
                ).get(
                    "page_type",
                    ""
                ),



            "description":

                page.get(
                    "page",
                    {}
                ).get(
                    "description",
                    ""
                ),




            # Counts

            "buttons":
                len(buttons),


            "inputs":
                len(inputs),


            "links":
                len(links),


            "forms":
                len(forms),


            "tables":
                len(page.get(
                    "tables",
                    []
                )),


            "dialogs":
                len(dialogs),



            "components":

            {

                "cards":

                    len(cards),


                "grids":

                    len(grids),


                "tabs":

                    len(
                        components.get(
                            "tabs",
                            []
                        )
                    )

            },




            # -------------------------
            # Component Knowledge
            # -------------------------


            "component_types":

                sorted({

                    c.get(
                        "type"
                    )

                    for c in cards

                    if c.get("type")

                }),



            "card_titles":

                sorted({

                    c.get(
                        "title",
                        ""
                    )

                    for c in cards

                    if c.get(
                        "title"
                    )

                }),




            "grid_columns":

                sorted({

                    column

                    for grid in grids

                    for column in grid.get(
                        "columns",
                        []
                    )

                }),




            "grid_actions":

                sorted({

                    action

                    for grid in grids

                    for action in grid.get(
                        "actions",
                        []
                    )

                }),



            "tabs":

                sorted(

                    components.get(
                        "tabs",
                        []
                    )

                ),




            "dialog_titles":

                sorted({

                    d.get(
                        "title",
                        ""
                    )

                    for d in components.get(
                        "dialogs",
                        []
                    )

                    if d.get(
                        "title"
                    )

                }),




            "dropdowns":

                components.get(
                    "dropdowns",
                    {}

                ),





            # -------------------------
            # Existing Knowledge
            # -------------------------


            "button_texts":

                sorted({

                    b.get(
                        "text",
                        ""
                    ).strip()

                    for b in buttons

                    if b.get(
                        "text",
                        ""
                    ).strip()

                }),




            "input_placeholders":

                sorted({

                    i.get(
                        "placeholder",
                        ""
                    ).strip()

                    for i in inputs

                    if i.get(
                        "placeholder"
                    )

                }),




            "navigation":

                sorted({

                    l.get(
                        "text",
                        ""
                    ).strip()

                    for l in links

                    if l.get(
                        "text",
                        ""
                    ).strip()

                }),




            "menu_items":

                sorted({

                    m.get(
                        "text",
                        ""
                    ).strip()

                    for m in menus

                    if m.get(
                        "text",
                        ""
                    ).strip()

                }),




            "headings_text":

                sorted({

                    h.get(
                        "text",
                        ""
                    ).strip()

                    for h in headings

                    if h.get(
                        "text"
                    )

                }),




            "validation_texts":

                sorted({

                    v.get(
                        "text",
                        ""
                    ).strip()

                    for v in validations

                    if v.get(
                        "text"
                    )

                })

        }