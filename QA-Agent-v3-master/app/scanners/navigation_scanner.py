from urllib.parse import urljoin, urlparse



class NavigationScanner:
    """
    Generic Navigation Scanner.

    Responsibilities:
    - Discover application navigation
    - Extract internal/external links
    - Detect menu candidates

    Supports:
    - Traditional websites
    - React / Angular / Vue SPA
    """



    def __init__(self, page):

        self.page = page


        parsed = urlparse(
            page.url
        )


        self.base_domain = (
            parsed.netloc
        )


        self.blocked_keywords = [

            "logout",
            "signout",
            "delete",
            "remove"

        ]


        self.blocked_extensions = [

            ".png",
            ".jpg",
            ".jpeg",
            ".svg",
            ".css",
            ".js",
            ".pdf"

        ]



    # =========================
    # NAVIGATION SCANNER V4
    # =========================


    def scan(self):

        print(
            "PAGE TITLE:",
            self.page.title()
        )

        print(
            "BODY LENGTH:",
            len(self.page.content())
        )

        print(
            self.page.content()[:1000]
        )
        print("Current URL:", self.page.url)

        print("READY STATE:",
      self.page.evaluate("document.readyState"))

        print("BODY CHILDREN:",
      self.page.locator("body *").count())

        print("HTML ELEMENTS:",
      self.page.locator("html *").count())
        print(
    "BODY TEXT:",
    self.page.locator("body").inner_text()[:300]
)

        print(
    self.page.content()[:1000]
)
        internal_links = set()

        external_links = set()

        menus = []

        interactive_elements = []



        selectors = [

    # Standard links
    "a",
    "a[href]",

    # SPA routing
    "[routerlink]",
    "[data-url]",
    "[data-href]",

    # Accessibility
    "[role='link']",
    "[role='menuitem']",

    # Generic navigation containers
    "nav a",
    "nav *",

    "aside a",
    "aside *",

    "header a",
    "header *",

    "footer a",

    # Menus
    "[role='navigation'] *",
    "[role='menu'] *",

    # Tabs
    "[role='tab']",

    # Buttons that may navigate
    "button",
    "[role='button']",

    # Generic clickable elements
    "[onclick]",
    "[tabindex]"
]

        for selector in selectors:


            try:


                elements = self.page.locator(
                    selector
                )


                count = elements.count()

                print(
                       f"[NAV DEBUG] {selector} -> {count}"
                     )



            except Exception:


                continue




            for i in range(count):


                try:


                    element = elements.nth(i)

                    tag = self.detect_type(element)

                    text = self.safe_text(element)

                    role = element.get_attribute("role")

                    classes = element.get_attribute("class")

                    element_info = {

                        "tag": tag,

                        "text": text,

                        "role": role,

                        "class": classes

                    }

                    if self.is_interactive_element(
                        element,
                        tag,
                        role
                    ):

                        interactive_elements.append(
                        element_info
                        )



                    href = (

                        element.get_attribute(
                            "href"
                        )

                        or

                        element.get_attribute(
                            "routerlink"
                        )

                        or

                        element.get_attribute(
                            "data-url"
                        )

                        or

                        element.get_attribute(
                            "data-href"
                        )

                    )

                    if href:

                        href = href.strip()

                        if href in [

                            "#",

                            "",

                            "javascript:void(0)",

                            "javascript:;"

                        ]:

                            href = None

                    if not href:

                     onclick = element.get_attribute("onclick")

                    if onclick:

                            if "location.href" in onclick:

                                try:

                                    href = onclick.split("'")[1]

                                except Exception:

                                 pass


                    if not href:

                        try:

                            href = element.evaluate(
                                """
                                (el) => {
                                    return (
                                        el.dataset.url ||
                                        el.dataset.href ||
                                        null
                                    );
                                }
                                """
                        )

                        except Exception:

                         pass


                    if not href:

                      continue


                    href = href.strip()


                    if href in [

                        "#",

                        "",

                        "javascript:void(0)",

                        "javascript:;"

                    ]:

                        continue


                    absolute = urljoin(

                        self.page.url,

                        href

                    )


                    normalized = self.normalize_url(

                        absolute

                    )



                    if not normalized:


                        continue



                    text = self.safe_text(

                        element

                    )
                    role = element.get_attribute("role") or ""

                    aria = element.get_attribute("aria-label") or ""

                    title = element.get_attribute("title") or ""



                    item = {

                        "text": text,

                        "href": normalized,

                        "type": self.detect_type(element),

                        "role": role,

                        "aria_label": aria,

                        "title": title

                    }

                    tag = item["type"]

                    if not self.is_interactive_element(
                        element,
                        tag,
                        role
                    ):
                        continue


                    if urlparse(
                        normalized
                    ).netloc == self.base_domain:



                        internal_links.add(

                            normalized

                        )



                        if self.is_menu_candidate(

                            element,

                            text

                        ):


                            menus.append(

                                item

                            )



                    else:


                        external_links.add(

                            normalized

                        )



                except Exception:


                    continue



        return {


            "menus":

                self.remove_duplicates(

                    menus

                ),



            "internal_links":

                sorted(

                    internal_links

                ),



            "external_links":

                sorted(

                    external_links

                ),

                "interactive_elements":
                     interactive_elements
        


        }
        # =========================
    # URL NORMALIZATION
    # =========================


    def normalize_url(
        self,
        url
    ):


        try:


            parsed = urlparse(
                url
            )



            path = parsed.path.lower()



            for ext in self.blocked_extensions:


                if path.endswith(ext):

                    return None



            # Remove query strings
            path = parsed.path.rstrip("/")


            if not path:

                path = "/"



            clean = (

                f"{parsed.scheme}://"

                f"{parsed.netloc}"

                f"{path}"

            )



            clean = clean.rstrip("/")



            lower = clean.lower()



            for word in self.blocked_keywords:


                if word in lower:

                    return None



            return clean



        except Exception:


            return None





    # =========================
    # MENU DETECTION
    # =========================


    def is_menu_candidate(
        self,
        element,
        text
    ):


        try:


            tag = element.evaluate(

                "(el)=>el.tagName.toLowerCase()"

            )


            parent = element.evaluate(

                "(el)=>el.parentElement.tagName.toLowerCase()"

            )



            if tag in [

                "a",

                "button"

            ]:

             return True
                 
            try:

                role = element.get_attribute("role")

                if role in [

                    "menuitem",

                    "tab",

                    "link",

                    "button"

                ]:

                  return True

            except Exception:

                pass



            if parent in [

                "nav",

                "aside",

                "header",

            ]:


                return True



            if text and len(text) < 40:


                return True



        except Exception:


            pass



        return False





    # =========================
    # TYPE DETECTION
    # =========================


    def detect_type(
        self,
        element
    ):


        try:


            return element.evaluate(

                "(el)=>el.tagName.toLowerCase()"

            )



        except Exception:


            return "unknown"





    # =========================
    # HELPERS
    # =========================


    def safe_text(
        self,
        element
    ):


        try:


            return (

                element.inner_text()

                .strip()

            )



        except Exception:


            return ""





    def remove_duplicates(
        self,
        items
    ):


        result = []

        seen = set()



        for item in items:


            key = item.get(

                "href"

            )



            if key not in seen:


                seen.add(

                    key

                )


                result.append(

                    item

                )



        return result
    
        # =========================
    # INTERACTIVE ELEMENT
    # =========================

    def is_interactive_element(
        self,
        element,
        tag,
        role
    ):
        try:

            if tag in [

            "a",
            "button",
            "input",
            "select",
            "textarea"

            ]:

               return True


            if role in [

            "button",
            "link",
            "menuitem",
            "tab",
            "option"

            ]:

               return True


            return False


        except Exception:

            return False