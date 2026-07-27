from typing import Any, Dict, List
from playwright.sync_api import Page


class ActionEngine:
    """
    Generic AI Action Discovery Engine

    Responsible for discovering possible user actions
    from any web application.

    Responsibilities:
    - Discover interactive elements
    - Detect navigation candidates
    - Classify user intent
    - Produce execution-ready metadata

    It DOES NOT execute actions.
    """

    def __init__(self, page: Page):

        self.page = page


    # =====================================================
    # Public API
    # =====================================================

    def discover_actions(self) -> List[Dict[str, Any]]:
        """
        Main entry point.

        Returns:
            List of discovered semantic actions
        """

        actions = []
        print("\n========== ACTION ENGINE ==========")
        print("ACTION PAGE URL:", self.page.url)
        print("BUTTONS:", self.page.locator("button").count())
        print("LINKS:", self.page.locator("a").count())
        print("INPUTS:", self.page.locator("input").count())
        print("==================================\n")


        actions.extend(
            self._discover_buttons()
        )


        actions.extend(
            self._discover_links()
        )


        actions.extend(
            self._discover_inputs()
        )


        actions.extend(
            self._discover_forms()
        )


        actions.extend(
            self._discover_clickable_components()
        )


        actions = self._deduplicate_actions(
            actions
        )


        return actions



    # =====================================================
    # Element Discovery
    # =====================================================


    def _discover_buttons(self):

        actions = []


        selectors = [

            "button",

            "[role='button']",

            "input[type='button']",

            "input[type='submit']"

        ]


        for selector in selectors:


            elements = self.page.locator(
                selector
            )


            count = elements.count()


            for index in range(count):

                element = elements.nth(index)


                action = self._analyze_element(
                    element,
                    "button"
                )


                if action:

                    actions.append(action)


        return actions



    # =====================================================
    # Links Discovery
    # =====================================================


    def _discover_links(self):

        actions = []


        selectors = [

            "a",

            "a[href]",

            "[role='link']"

        ]


        for selector in selectors:


            elements = self.page.locator(
                selector
            )


            count = elements.count()


            for index in range(count):

                element = elements.nth(index)


                action = self._analyze_element(
                    element,
                    "link"
                )


                if action:

                    actions.append(action)


        return actions



    # =====================================================
    # Inputs Discovery
    # =====================================================


    def _discover_inputs(self):

        actions = []


        selectors = [

            "input",

            "textarea",

            "select",

            "[contenteditable='true']"

        ]


        for selector in selectors:


            elements = self.page.locator(
                selector
            )


            count = elements.count()


            for index in range(count):

                element = elements.nth(index)


                action = self._analyze_element(
                    element,
                    "input"
                )


                if action:

                    actions.append(action)


        return actions



    # =====================================================
    # Forms Discovery
    # =====================================================


    def _discover_forms(self):

        actions = []


        forms = self.page.locator(
            "form"
        )


        count = forms.count()


        for index in range(count):

            form = forms.nth(index)


            action = self._analyze_element(
                form,
                "form"
            )


            if action:

                actions.append(action)


        return actions



    # =====================================================
    # Generic Clickable Components
    # =====================================================


    def _discover_clickable_components(self):

        actions = []


        selectors = [

            "[onclick]",

            "[data-url]",

            "[data-href]",

            "[data-link]",

            "[data-route]",

            "[routerLink]",

            "[router-link]",

            "[to]",

            ".menu-item",

            ".nav-item",

            ".sidebar-item",

            ".tab",

            "[role='menuitem']",

            "[role='tab']"

        ]


        for selector in selectors:


            elements = self.page.locator(
                selector
            )


            count = elements.count()


            for index in range(count):

                element = elements.nth(index)


                action = self._analyze_element(
                    element,
                    "component"
                )


                if action:

                    actions.append(action)



        return actions



    # =====================================================
    # Element Analyzer
    # =====================================================


    def _analyze_element(
        self,
        element,
        element_type
    ):

        try:

            if not element.is_visible():

                return None

        except Exception:

            pass


        metadata = self._extract_metadata(
            element
        )


        if not metadata:

            return None


        semantic_text = " ".join([

            metadata.get(
                "text",
                ""
            ),

            metadata.get(
                "aria",
                ""
            ),

            metadata.get(
                "title",
                ""
            ),

            metadata.get(
                "placeholder",
                ""
            ),

            metadata.get(
                "attributes",
                ""
            )

        ]).lower()



        classification = self._classify_action(
        semantic_text,
        element_type,
        metadata
        )

        navigation = metadata.get("navigation", {})

        if navigation.get("detected"):
            print(
            "NAV:",
            metadata.get("text"),
            "->",
            navigation.get("target")
        )

            return {

                "element_type": element_type,

                "action": classification["action"],

                "target": metadata.get("navigation", {}).get("target"),

                "executed": False,

                "confidence": classification["confidence"],

                "risk": classification["risk"],

                "requires_input": classification["requires_input"],

                "may_navigate": classification["may_navigate"],

                "may_open_dialog": classification["may_open_dialog"],

                "metadata": metadata,

                "locator": self._build_locator(element)

            }
    # =====================================================
    # Metadata Extraction
    # =====================================================

    def _extract_metadata(self, element):

        metadata = {

            "text": "",
            "aria": "",
            "title": "",
            "placeholder": "",
            "tag": "",
            "attributes": "",
            "navigation": {}

        }


        try:

            metadata["tag"] = element.evaluate(
                "(el)=>el.tagName.toLowerCase()"
            )

        except Exception:

            pass



        try:

            metadata["text"] = (
                element.inner_text() or ""
            ).strip()

        except Exception:

            pass



        for attr in [

            "aria-label",
            "title",
            "placeholder"

        ]:

            try:

                value = element.get_attribute(
                    attr
                )

                if value:

                    metadata[
                        attr.replace("-", "_")
                    ] = value


            except Exception:

                pass



        metadata["navigation"] = (
            self._detect_navigation(element)
        )



        try:

            attributes = element.evaluate(
                """
                (el)=>{

                    let result=[];

                    for(
                        let attr of el.attributes
                    ){
                        result.push(
                            attr.name +
                            "=" +
                            attr.value
                        );
                    }

                    return result.join(" ");

                }
                """
            )


            metadata["attributes"] = attributes or ""


        except Exception:

            pass



        return metadata



    # =====================================================
    # Navigation Detection
    # =====================================================

    def _detect_navigation(self, element):

        navigation = {

            "detected": False,

            "type": None,

            "target": None,

            "source": None

        }



        attributes = [

            "href",

            "routerLink",

            "router-link",

            "to",

            "data-url",

            "data-href",

            "data-link",

            "data-route",

            "onclick"

        ]



        for attr in attributes:


            try:

                value = element.get_attribute(
                    attr
                )


            except Exception:

                value = None

            print("ATTR:", attr, "=", value)

            if not value:

                continue

            value = value.strip()

            print("FOUND NAV:", attr, "->", value)



            # -----------------------------
            # Normal href
            # -----------------------------

            if attr == "href":
                print("HREF TARGET:", value)



                navigation.update({

                    "detected": True,

                    "type": "href",

                    "target": value,

                    "source": attr

                })


                return navigation



            # -----------------------------
            # Angular
            # -----------------------------

            if attr == "routerLink":


                navigation.update({

                    "detected": True,

                    "type": "angular_route",

                    "target": value,

                    "source": attr

                })


                return navigation



            # -----------------------------
            # Vue
            # -----------------------------

            if attr == "router-link":


                navigation.update({

                    "detected": True,

                    "type": "vue_route",

                    "target": value,

                    "source": attr

                })


                return navigation



            # -----------------------------
            # React Router
            # -----------------------------

            if attr == "to":


                navigation.update({

                    "detected": True,

                    "type": "react_route",

                    "target": value,

                    "source": attr

                })


                return navigation



            # -----------------------------
            # Data Routes
            # -----------------------------

            if attr in [

                "data-url",

                "data-href",

                "data-link",

                "data-route"

            ]:


                navigation.update({

                    "detected": True,

                    "type": "data_route",

                    "target": value,

                    "source": attr

                })


                return navigation



            # -----------------------------
            # JavaScript Navigation
            # -----------------------------

            if attr == "onclick":


                js_navigation = (
                    self._parse_javascript_navigation(
                        value
                    )
                )


                if js_navigation:


                    return js_navigation



        return navigation




    # =====================================================
    # JavaScript Navigation Parser
    # =====================================================

    def _parse_javascript_navigation(
        self,
        script
    ):


        script = script.lower()



        patterns = {


            "window.location":

                "javascript_location",


            "location.href":

                "javascript_href",


            "location.assign":

                "javascript_assign",


            "location.replace":

                "javascript_replace",


            "history.pushstate":

                "history_push",


            "history.replacestate":

                "history_replace"


        }



        for pattern, nav_type in patterns.items():


            if pattern in script:


                return {


                    "detected": True,

                    "type": nav_type,

                    "target": script,

                    "source": "onclick"

                }



        return None
    
        # =====================================================
    # Action Classification Engine
    # =====================================================

    def _classify_action(
        self,
        text,
        element_type,
        metadata
    ):

        result = {

            "action": "unknown",

            "confidence": 0.50,

            "risk": "low",

            "requires_input": False,

            "may_navigate": False,

            "may_open_dialog": False

        }


        navigation = metadata.get(
            "navigation",
            {}
        )


        # ---------------------------------
        # Navigation Detection
        # ---------------------------------

        if navigation.get(
            "detected"
        ):


            result.update({

                "action": "navigate",

                "confidence": 0.95,

                "may_navigate": True

            })


            return result



        # ---------------------------------
        # Element Based Defaults
        # ---------------------------------

        if element_type == "link":


            result.update({

                "action": "navigate",

                "confidence": 0.90,

                "may_navigate": True

            })


            return result



        if element_type == "input":


            input_type = ""


            try:

                input_type = (
                    metadata.get(
                        "attributes",
                        ""
                    )
                ).lower()


            except Exception:

                pass



            if "submit" in input_type:


                result.update({

                    "action": "submit",

                    "confidence": 0.90

                })


            else:


                result.update({

                    "action": "fill",

                    "confidence": 0.90,

                    "requires_input": True

                })


            return result



        # ---------------------------------
        # Semantic Keywords
        # ---------------------------------

        keywords = {


            # Navigation

            "home": "navigate",

            "dashboard": "navigate",

            "profile": "navigate",

            "settings": "navigate",


            # Authentication

            "login": "submit",

            "sign in": "submit",

            "logout": "submit",

            "register": "create",


            # Create

            "add": "create",

            "new": "create",

            "create": "create",

            "upload": "upload",


            # Update

            "edit": "edit",

            "update": "edit",

            "modify": "edit",


            # Delete

            "delete": "delete",

            "remove": "delete",


            # Search

            "search": "search",

            "find": "search",


            # Filter

            "filter": "filter",

            "sort": "filter",


            # Export / Import

            "export": "export",

            "download": "download",

            "import": "import",


            # Dialog

            "open": "open_dialog",

            "view": "view",

            "details": "view",


            # Pagination

            "next": "pagination",

            "previous": "pagination",

            "page": "pagination",


            # Refresh

            "refresh": "refresh"

        }



        for keyword, action in keywords.items():


            if keyword in text:


                result["action"] = action

                result["confidence"] = 0.85

                break



        # ---------------------------------
        # Risk Calculation
        # ---------------------------------

        if result["action"] in [

            "delete"

        ]:


            result["risk"] = "high"



        elif result["action"] in [

            "create",

            "edit",

            "submit",

            "upload"

        ]:


            result["risk"] = "medium"

            result["requires_input"] = True



        elif result["action"] == "open_dialog":


            result["may_open_dialog"] = True



        return result




    # =====================================================
    # Locator Builder
    # =====================================================

    def _build_locator(
        self,
        element
    ):


        strategies = [

            "aria-label",

            "placeholder",

            "name",

            "id",

            "title"

        ]


        try:

            text = (
                element.inner_text() or ""
            ).strip()


            if text:


                return {

                    "strategy": "text",

                    "value": text

                }


        except Exception:

            pass



        for attr in strategies:


            try:

                value = (
                    element.get_attribute(
                        attr
                    )
                )


                if value:


                    return {

                        "strategy": attr,

                        "value": value

                    }


            except Exception:

                continue



        return {


            "strategy": "css",

            "value": "unknown"

        }




    # =====================================================
    # Deduplicate Actions
    # =====================================================

    def _deduplicate_actions(
        self,
        actions
    ):


        unique = []

        fingerprints = set()



        for action in actions:


            metadata = action.get(
                "metadata",
                {}
            )


            text = metadata.get(
                "text",
                ""
            )


            element_type = action.get(
                "element_type",
                ""
            )


            fingerprint = (

                element_type,

                action.get(
                    "action"
                ),

                text

            )



            if fingerprint in fingerprints:

                continue



            fingerprints.add(
                fingerprint
            )


            unique.append(
                action
            )



        return unique