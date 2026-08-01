from typing import Dict


class ElementScanner:

    """
    Generic Web Element Scanner V3

    Responsibility:
    - Discover UI elements
    - Normalize element metadata
    - Provide semantic hints

    Does NOT:
    - Generate test cases
    - Detect workflows
    - Decide business rules
    """


    def __init__(self, page):

        self.page = page



    # =========================
    # MAIN SCAN
    # =========================


    def scan(self) -> Dict:

        print("ELEMENT SCANNER V3 SAFE LOADED")


        result = {

            "buttons": [],
            "inputs": [],
            "links": [],
            "selects": [],
            "textareas": [],
            "checkboxes": [],
            "radio_buttons": []

        }


        try:
            result["buttons"] = self._scan_buttons()
        except Exception as e:
            print("buttons scan failed:", e)


        try:
            result["inputs"] = self._scan_inputs()
        except Exception as e:
            print("inputs scan failed:", e)


        try:
            result["links"] = self._scan_links()
        except Exception as e:
            print("links scan failed:", e)


        try:
            result["selects"] = self._scan_selects()
        except Exception as e:
            print("select scan failed:", e)


        try:
            result["textareas"] = self._scan_textareas()
        except Exception as e:
            print("textarea scan failed:", e)


        try:
            result["checkboxes"] = self._scan_checkboxes()
        except Exception as e:
            print("checkbox scan failed:", e)


        try:
            result["radio_buttons"] = self._scan_radios()
        except Exception as e:
            print("radio scan failed:", e)



        result["summary"] = {

            "buttons":
                len(result["buttons"]),

            "inputs":
                len(result["inputs"]),

            "links":
                len(result["links"]),

            "selects":
                len(result["selects"])

        }


        return result




# =========================
# BUTTONS
# =========================


    def _scan_buttons(self):

        elements = []


        locator = self.page.locator(
            "button, [role='button'], input[type='button'], input[type='submit']"
        )


        count = locator.count()


        for index in range(count):

            try:

                element = locator.nth(index)


                data = self._extract_common(
                    element
                )


                text = self._safe_text(
                    element
                )


                data.update({

                    "element_type":
                        "button",


                    "text":
                        text,


                    "semantic_hints":
                    {

                        "possible_actions":
                            self._detect_actions(
                                text
                            )

                    }

                })


                if self._is_meaningful(data):

                    elements.append(data)


            except Exception as e:

                print(
                    f"button {index} skipped:",
                    e
                )


        return elements




# =========================
# INPUTS
# =========================


    def _scan_inputs(self):

        elements = []


        locator = self.page.locator(
            "input"
        )


        count = locator.count()



        for index in range(count):

            try:


                element = locator.nth(index)



                input_type = (
                    self._safe_attribute(
                        element,
                        "type"
                    )
                    or
                    "text"
                )



                if input_type in [
                    "checkbox",
                    "radio"
                ]:

                    continue



                data = self._extract_common(
                    element
                )



                data.update({

                    "element_type":
                        "input",


                    "input_type":
                        input_type,


                    "value":
                        self._safe_input_value(
                            element
                        ),


                    "placeholder":
                        self._safe_attribute(
                            element,
                            "placeholder"
                        ),


                    "required":
                        self._has_attribute(
                            element,
                            "required"
                        ),


                    "readonly":
                        self._has_attribute(
                            element,
                            "readonly"
                        ),


                    "semantic_hints":
                    {

                        "possible_purpose":
                            self._detect_input_purpose(
                                element,
                                input_type
                            )

                    }


                })



                if self._is_meaningful(data):

                    elements.append(data)



            except Exception as e:

                print(
                    f"input {index} skipped:",
                    e
                )



        return elements
    # =========================
# LINKS
# =========================


    def _scan_links(self):

        elements = []
        seen = set()

        locator = self.page.locator(
            "a"
        )


        count = locator.count()


        for index in range(count):

            try:

                element = locator.nth(index)


                data = self._extract_common(
                    element
                )


                text = self._safe_text(
                    element
                )


                data.update({

                    "element_type":
                        "link",


                    "text":
                        text,


                    "href":
                        self._safe_attribute(
                            element,
                            "href"
                        ),


                    "semantic_hints":
                    {

                        "possible_actions":
                            self._detect_actions(
                                text
                            )

                    }

                })



                if self._is_meaningful(data):
                    href = (data.get("href") or "").strip()
                    text = (data.get("text") or "").strip() 

                    key = (href, text)

                    if key in seen:
                        continue

                    seen.add(key)

                    elements.append(data)



            except Exception as e:

                print(
                    f"link {index} skipped:",
                    e
                )


        return elements





# =========================
# SELECT DROPDOWN
# =========================


    def _scan_selects(self):

        elements = []


        locator = self.page.locator(
            "select"
        )


        count = locator.count()



        for index in range(count):

            try:


                element = locator.nth(index)


                data = self._extract_common(
                    element
                )


                options = element.locator(
                    "option"
                )


                values = []



                for i in range(options.count()):

                    try:

                        values.append(
                            options.nth(i)
                            .inner_text()
                            .strip()
                        )

                    except:

                        continue



                data.update({

                    "element_type":
                        "select",


                    "options":
                        values,


                    "required":
                        self._has_attribute(
                            element,
                            "required"
                        )

                })



                if self._is_meaningful(data):

                    elements.append(data)



            except Exception as e:

                print(
                    f"select {index} skipped:",
                    e
                )



        return elements





# =========================
# TEXTAREA
# =========================


    def _scan_textareas(self):

        elements = []


        locator = self.page.locator(
            "textarea"
        )


        count = locator.count()



        for index in range(count):

            try:

                element = locator.nth(index)


                data = self._extract_common(
                    element
                )



                data.update({

                    "element_type":
                        "textarea",


                    "placeholder":
                        self._safe_attribute(
                            element,
                            "placeholder"
                        ),


                    "required":
                        self._has_attribute(
                            element,
                            "required"
                        )

                })



                if self._is_meaningful(data):

                    elements.append(data)



            except Exception as e:

                print(
                    f"textarea {index} skipped:",
                    e
                )



        return elements





# =========================
# CHECKBOX
# =========================


    def _scan_checkboxes(self):

        elements = []


        locator = self.page.locator(
            "input[type='checkbox']"
        )


        count = locator.count()



        for index in range(count):

            try:


                element = locator.nth(index)


                data = self._extract_common(
                    element
                )


                data.update({

                    "element_type":
                        "checkbox",


                    "checked":
                        self._safe_checked(
                            element
                        )

                })



                if self._is_meaningful(data):

                    elements.append(data)



            except Exception as e:

                print(
                    f"checkbox {index} skipped:",
                    e
                )



        return elements





# =========================
# RADIO BUTTONS
# =========================


    def _scan_radios(self):

        elements = []


        locator = self.page.locator(
            "input[type='radio']"
        )


        count = locator.count()



        for index in range(count):

            try:


                element = locator.nth(index)


                data = self._extract_common(
                    element
                )



                data.update({

                    "element_type":
                        "radio",


                    "checked":
                        self._safe_checked(
                            element
                        )

                })



                if self._is_meaningful(data):

                    elements.append(data)



            except Exception as e:

                print(
                    f"radio {index} skipped:",
                    e
                )



        return elements
    
# =========================
# COMMON EXTRACTION
# =========================


    def _extract_common(self, element):

        return {

            "tag":
                self._safe_evaluate(
                    element,
                    "(el)=>el.tagName.toLowerCase()"
                ),


            "id":
                self._safe_attribute(
                    element,
                    "id"
                ),


            "name":
                self._safe_attribute(
                    element,
                    "name"
                ),


            "role":
                self._safe_attribute(
                    element,
                    "role"
                ),


            "aria_label":
                self._safe_attribute(
                    element,
                    "aria-label"
                ),


            "title":
                self._safe_attribute(
                    element,
                    "title"
                ),


            "data_testid":
                (
                    self._safe_attribute(
                        element,
                        "data-testid"
                    )
                    or
                    self._safe_attribute(
                        element,
                        "data-test"
                    )
                ),


            "class":
                self._safe_attribute(
                    element,
                    "class"
                ),


            "visible":
                self._is_visible(
                    element
                ),


            "locator":
                self._build_locator(
                    element
                ),


            "label":
                self._find_label(
                    element
                )

        }





# =========================
# SAFE LOCATOR BUILDER
# =========================


    def _build_locator(self, element):

        try:


            test_id = (
                self._safe_attribute(
                    element,
                    "data-testid"
                )
                or
                self._safe_attribute(
                    element,
                    "data-test"
                )
            )


            if test_id:

                return {

                    "strategy":
                        "data-testid",

                    "value":
                        f"[data-testid='{test_id}']"

                }



            element_id = self._safe_attribute(
                element,
                "id"
            )


            if element_id:

                return {

                    "strategy":
                        "id",

                    "value":
                        f"#{element_id}"

                }



            name = self._safe_attribute(
                element,
                "name"
            )


            if name:

                return {

                    "strategy":
                        "name",

                    "value":
                        f"[name='{name}']"

                }



            aria = self._safe_attribute(
                element,
                "aria-label"
            )


            if aria:

                return {

                    "strategy":
                        "aria-label",

                    "value":
                        f"[aria-label='{aria}']"

                }




            placeholder = self._safe_attribute(
                element,
                "placeholder"
            )


            if placeholder:

                return {

                    "strategy":
                        "placeholder",

                    "value":
                        f"[placeholder='{placeholder}']"

                }



            text = self._safe_text(
                element
            )


            if text:

                return {

                    "strategy":
                        "text",

                    "value":
                        text[:100]

                }



        except Exception as e:

            print(
                "locator build failed:",
                e
            )



        return {

            "strategy":
                "css",

            "value":
                "unknown"

        }





# =========================
# LABEL DETECTION
# =========================


    def _find_label(self, element):

        try:


            element_id = self._safe_attribute(
                element,
                "id"
            )


            if element_id:


                label = self.page.locator(
                    f"label[for='{element_id}']"
                )


                if label.count():

                    return (
                        label.first
                        .inner_text(
                            timeout=1000
                        )
                        .strip()
                    )



            parent = element.locator(
                "xpath=ancestor::label"
            )


            if parent.count():

                return (
                    parent.first
                    .inner_text(
                        timeout=1000
                    )
                    .strip()
                )


        except:

            pass



        return None





# =========================
# ACTION DETECTION
# =========================


    def _detect_actions(self, text):

        if not text:

            return []


        value = text.lower()



        mapping = {


            "create":
            [
                "add",
                "new",
                "create",
                "register"
            ],


            "save":
            [
                "save",
                "submit",
                "confirm",
                "apply"
            ],


            "update":
            [
                "edit",
                "update",
                "modify"
            ],


            "delete":
            [
                "delete",
                "remove",
                "trash"
            ],


            "search":
            [
                "search",
                "find",
                "lookup"
            ],


            "reset":
            [
                "reset",
                "clear"
            ],


            "export":
            [
                "export",
                "download"
            ]

        }



        result = []


        for action, words in mapping.items():

            for word in words:

                if word in value:

                    result.append(
                        action
                    )

                    break



        return result





# =========================
# INPUT PURPOSE
# =========================


    def _detect_input_purpose(
            self,
            element,
            input_type
    ):


        text = " ".join([


            str(
                self._safe_attribute(
                    element,
                    "name"
                )
            ),


            str(
                self._safe_attribute(
                    element,
                    "placeholder"
                )
            ),


            str(
                self._find_label(
                    element
                )
            )


        ]).lower()



        if "email" in text:

            return "email"



        if "password" in text:

            return "password"



        if "search" in text:

            return "search"



        if "phone" in text:

            return "phone"



        if input_type == "date":

            return "date"



        return "unknown"





# =========================
# SAFE HELPERS
# =========================


    def _safe_attribute(
            self,
            element,
            attribute
    ):


        try:

            return element.get_attribute(
                attribute,
                timeout=1500
            )


        except:

            return None





    def _safe_text(self, element):

        try:

            return (
                element.inner_text(
                    timeout=1500
                )
                .strip()
            )

        except:

            return ""





    def _safe_input_value(self, element):

        try:

            return element.input_value(
                timeout=1500
            )

        except:

            return None





    def _safe_checked(self, element):

        try:

            return element.is_checked(
                timeout=1500
            )

        except:

            return False





    def _safe_evaluate(
            self,
            element,
            script
    ):

        try:

            return element.evaluate(
                script
            )

        except:

            return None





    def _is_visible(self, element):

        try:

            return element.is_visible(
                timeout=1000
            )

        except:

            return False





    def _has_attribute(
            self,
            element,
            attribute
    ):

        return (
            self._safe_attribute(
                element,
                attribute
            )
            is not None
        )





    def _is_meaningful(self, data):

        fields = [

            "text",
            "id",
            "name",
            "role",
            "aria_label",
            "placeholder",
            "title",
            "data_testid",
            "label"

        ]


        for field in fields:

            if data.get(field):

                return True



        return False