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


        internal_links = set()

        external_links = set()

        menus = []



        selectors = [


            "a",

            "a[href]",

            "[routerlink]",

            "[data-url]",

            "[data-href]",

            "[role='link']",


            "[role='menuitem']",


            "button",


            "nav a",


            "aside a",


            ".oxd-main-menu-item",


            ".oxd-topbar-body-nav-tab-item"


        ]



        for selector in selectors:


            try:


                elements = self.page.locator(
                    selector
                )


                count = elements.count()



            except Exception:


                continue




            for i in range(count):


                try:


                    element = elements.nth(i)



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



                    if not href:


                        onclick = element.get_attribute(
                            "onclick"
                        )


                        if onclick and "/web/index.php/" in onclick:


                            href = onclick.split("'")[1]



                    if not href:


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



                    item = {


                        "text":

                            text,


                        "href":

                            normalized,


                        "type":

                            self.detect_type(

                                element

                            )

                    }



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

                )


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



            if tag == "a":

                return True



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