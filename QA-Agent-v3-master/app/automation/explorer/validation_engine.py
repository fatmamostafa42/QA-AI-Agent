from __future__ import annotations

import time
from typing import Any, Dict, Optional

from playwright.sync_api import (
    Page,
    Error,
    TimeoutError,
)


class ValidationEngine:
    """
    Generic Validation Engine

    Responsible for validating the result of any executed action.

    Features
    --------
    - URL change detection
    - DOM change detection
    - Success message detection
    - Error message detection
    - Dialog detection
    - Download detection
    - Upload detection
    - Screenshot on failure
    - Execution timing
    - Validation scoring

    Completely generic.

    No application-specific logic.
    """

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(self, page: Page):

        self.page = page

        self._before_url = ""
        self._before_dom = ""

    # =====================================================
    # Snapshot
    # =====================================================

    def capture_before_action(self):

        self._before_url = self.page.url

        try:

            self._before_dom = self.page.locator(
                "body"
            ).inner_html()

        except Exception:

            self._before_dom = ""

    # =====================================================
    # Validate
    # =====================================================

    def validate(self) -> Dict[str, Any]:

        started = time.perf_counter()

        result = {

            "success": True,

            "score": 100,

            "execution_time_ms": 0,

            "url_changed": False,

            "dom_changed": False,

            "dialog_opened": False,

            "download_started": False,

            "upload_detected": False,

            "success_message": None,

            "error_message": None,

            "redirected": False,

            "screenshot": None,

            "warnings": [],

            "errors": []

        }

        try:

            result["url_changed"] = self._url_changed()

            result["dom_changed"] = self._dom_changed()

            success = self._detect_success_message()

            error = self._detect_error_message()

            if success:

                result["success_message"] = success

            if error:

                result["success"] = False

                result["error_message"] = error

                result["score"] -= 40

            result["dialog_opened"] = self._dialog_opened()

            result["download_started"] = self._download_detected()

            result["upload_detected"] = self._upload_detected()

            result["redirected"] = (
                self.page.url != self._before_url
            )

            if (
                not result["success"]
                and result["screenshot"] is None
            ):

                result["screenshot"] = (
                    self._capture_screenshot()
                )

        except Exception as ex:

            result["success"] = False

            result["score"] = 0

            result["errors"].append(str(ex))

        finally:

            result["execution_time_ms"] = round(

                (time.perf_counter() - started)
                * 1000,

                2

            )

        return result

    # =====================================================
    # URL
    # =====================================================

    def _url_changed(self):

        return self.page.url != self._before_url

    # =====================================================
    # DOM
    # =====================================================

    def _dom_changed(self):

        try:

            current = self.page.locator(
                "body"
            ).inner_html()

            return current != self._before_dom

        except Exception:

            return False
            # =====================================================
    # Success Detection
    # =====================================================

    SUCCESS_SELECTORS = [

        ".toast-success",
        ".alert-success",
        ".success",
        ".notification-success",
        ".swal2-success",
        ".message-success",
        ".ant-message-success",
        ".MuiAlert-standardSuccess",
        ".v-alert--success",
        "[role='alert']",
        "[role='status']"

    ]

    SUCCESS_KEYWORDS = [

        "success",
        "successful",
        "saved",
        "created",
        "updated",
        "deleted",
        "completed",
        "done",
        "submitted",
        "uploaded",
        "imported",
        "exported",
        "approved",
        "accepted"

    ]

    def _detect_success_message(self):

        # CSS Selectors

        for selector in self.SUCCESS_SELECTORS:

            try:

                locator = self.page.locator(selector)

                if locator.count() == 0:
                    continue

                text = locator.first.inner_text().strip()

                if text:

                    return text

            except Exception:

                pass

        # Generic Body Search

        try:

            body = self.page.locator(
                "body"
            ).inner_text().lower()

            for keyword in self.SUCCESS_KEYWORDS:

                if keyword in body:

                    return keyword

        except Exception:

            pass

        return None

    # =====================================================
    # Error Detection
    # =====================================================

    ERROR_SELECTORS = [

        ".toast-error",
        ".alert-danger",
        ".alert-error",
        ".error",
        ".validation-error",
        ".field-error",
        ".invalid-feedback",
        ".swal2-error",
        ".notification-error",
        ".ant-message-error",
        ".MuiAlert-standardError"

    ]

    ERROR_KEYWORDS = [

        "error",
        "failed",
        "invalid",
        "required",
        "already exists",
        "duplicate",
        "unauthorized",
        "forbidden",
        "denied",
        "not allowed",
        "incorrect",
        "cannot",
        "unable",
        "warning"

    ]

    def _detect_error_message(self):

        for selector in self.ERROR_SELECTORS:

            try:

                locator = self.page.locator(selector)

                if locator.count() == 0:
                    continue

                text = locator.first.inner_text().strip()

                if text:

                    return text

            except Exception:

                pass

        try:

            body = self.page.locator(
                "body"
            ).inner_text().lower()

            for keyword in self.ERROR_KEYWORDS:

                if keyword in body:

                    return keyword

        except Exception:

            pass

        return None

    # =====================================================
    # Dialog Detection
    # =====================================================

    DIALOG_SELECTORS = [

        "[role='dialog']",
        ".modal",
        ".dialog",
        ".popup",
        ".drawer",
        ".offcanvas",
        ".swal2-popup"

    ]

    def _dialog_opened(self):

        for selector in self.DIALOG_SELECTORS:

            try:

                locator = self.page.locator(selector)

                if locator.count() > 0:

                    if locator.first.is_visible():

                        return True

            except Exception:

                pass

        return False

    # =====================================================
    # Download Detection
    # =====================================================

    def _download_detected(self) -> bool:
        """
        Generic download detection.

        This method checks whether the page contains elements
        that are likely to trigger a download.

        Actual download execution should be handled later by
        ExecutionEngine using Playwright's expect_download().

        Compatible with:
            - Traditional websites
            - SPA applications
            - Playwright
            - Future Appium Adapter
        """

        selectors = [

            "a[download]",

            "button[download]",

            "[data-download]",

            "[download]",

            "a[href$='.pdf']",
            "a[href$='.csv']",
            "a[href$='.xlsx']",
            "a[href$='.xls']",
            "a[href$='.zip']",
            "a[href$='.doc']",
            "a[href$='.docx']",

        ]

        try:

            for selector in selectors:

                locator = self.page.locator(selector)

                if locator.count() > 0:

                    return True

        except Exception:

            pass

        return False

    # =====================================================
    # Upload Detection
    # =====================================================

    def _upload_detected(self):

        try:

            locator = self.page.locator(
                "input[type=file]"
            )

            return locator.count() > 0

        except Exception:

            return False
            # =====================================================
    # Screenshot
    # =====================================================

    def _capture_screenshot(self):

        try:

            filename = (
                "storage/screenshots/"
                f"validation_{int(time.time())}.png"
            )

            self.page.screenshot(

                path=filename,

                full_page=True

            )

            return filename

        except Exception:

            return None

    # =====================================================
    # Validation Score
    # =====================================================

    def calculate_score(
        self,
        result: Dict[str, Any]
    ) -> int:

        score = 100

        if result.get("error_message"):
            score -= 40

        if not result.get("dom_changed"):
            score -= 10

        if not result.get("url_changed"):
            score -= 5

        if result.get("dialog_opened"):
            score += 5

        if result.get("success_message"):
            score += 10

        if score > 100:
            score = 100

        if score < 0:
            score = 0

        return score

    # =====================================================
    # Retry Recommendation
    # =====================================================

    def should_retry(
        self,
        result: Dict[str, Any]
    ) -> bool:

        if result.get("success"):
            return False

        if result.get("execution_time_ms", 0) > 30000:
            return True

        if result.get("error_message"):

            text = result["error_message"].lower()

            retry_keywords = [

                "timeout",
                "temporarily",
                "network",
                "connection",
                "try again",
                "server error"

            ]

            for keyword in retry_keywords:

                if keyword in text:

                    return True

        return False

    # =====================================================
    # Execution Summary
    # =====================================================

    def summarize(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "passed": result.get("success", False),

            "score": self.calculate_score(result),

            "retry": self.should_retry(result),

            "execution_time_ms": result.get(
                "execution_time_ms",
                0
            ),

            "success_message": result.get(
                "success_message"
            ),

            "error_message": result.get(
                "error_message"
            ),

            "warnings": result.get(
                "warnings",
                []
            ),

            "errors": result.get(
                "errors",
                []
            ),

            "screenshot": result.get(
                "screenshot"
            )

        }

    # =====================================================
    # Utilities
    # =====================================================

    def wait_for_idle(
        self,
        timeout: int = 5000
    ):

        try:

            self.page.wait_for_load_state(

                "networkidle",

                timeout=timeout

            )

        except TimeoutError:

            pass

        except Error:

            pass

    def page_title(self):

        try:

            return self.page.title()

        except Exception:

            return ""

    def current_url(self):

        try:

            return self.page.url

        except Exception:

            return ""

    def page_html(self):

        try:

            return self.page.content()

        except Exception:

            return ""

    def page_text(self):

        try:

            return self.page.locator(
                "body"
            ).inner_text()

        except Exception:

            return ""

    # =====================================================
    # End
    # =====================================================