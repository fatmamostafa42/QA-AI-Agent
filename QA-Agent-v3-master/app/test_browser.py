from app.automation.playwright.browser import BrowserManager

manager = BrowserManager(headless=False)

browser = manager.start()

context = manager.new_context()

page = context.new_page()

page.goto("https://example.com")

print(page.title())

manager.stop()