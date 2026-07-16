from playwright.sync_api import Page

from app.scanners.locator_builder import LocatorBuilder


class TableScanner:
    """
    Scans HTML tables and grid-like components.
    """

    def __init__(self, page: Page):
        self.page = page
        self.locator_builder = LocatorBuilder(page)

    def scan(self):

        tables = []

        for table in self.page.locator("table").all():

            tables.append({
                "locator": self.locator_builder.build(table),
                "headers": self._headers(table),
                "rows": self._rows_count(table),
                "columns": self._columns_count(table),
                "actions": self._actions(table),
                "pagination": self._has_pagination(table),
                "search": self._has_search(table),
                "filters": self._has_filters(table)
            })

        return tables

    def _headers(self, table):

        headers = []

        for th in table.locator("thead th").all():

            text = th.inner_text().strip()

            if text:
                headers.append(text)

        return headers

    def _rows_count(self, table):

        return table.locator("tbody tr").count()

    def _columns_count(self, table):

        headers = table.locator("thead th").count()

        if headers:
            return headers

        rows = table.locator("tbody tr").first

        if rows.count():
            return rows.locator("td").count()

        return 0

    def _actions(self, table):

        actions = set()

        keywords = {
            "Edit",
            "Delete",
            "View",
            "Details",
            "Remove",
            "Update",
            "Approve",
            "Reject",
            "Download"
        }

        for button in table.locator("button").all():

            text = button.inner_text().strip()

            if text in keywords:
                actions.add(text)

        return sorted(actions)

    def _has_pagination(self, table):

        return (
            self.page.locator(
                ".pagination, .pager, .oxd-pagination"
            ).count()
            > 0
        )

    def _has_search(self, table):

        return (
            self.page.locator(
                "input[type='search']"
            ).count()
            > 0
        )

    def _has_filters(self, table):

        return (
            self.page.locator(
                "select, input[type='date'], input[type='checkbox']"
            ).count()
            > 0
        )