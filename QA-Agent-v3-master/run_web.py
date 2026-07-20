from app.automation.playwright.browser import BrowserManager
from app.automation.playwright.login import LoginManager
from app.automation.playwright.crawler import Crawler

from app.exporters.json_exporter import JsonExporter
from app.exporters.knowledge_exporter import KnowledgeExporter
from app.exporters.requirements_exporter import RequirementsExporter
from app.exporters.features_exporter import FeaturesExporter
from app.exporters.scenarios_exporter import ScenariosExporter
from app.exporters.testcase_exporter import TestCaseExporter

from app.knowledge.knowledge_builder import KnowledgeBuilder
from app.analyzers.requirement_analyzer import RequirementAnalyzer
from app.analyzers.feature_splitter import FeatureSplitter
from app.analyzers.scenario_generator import ScenarioGenerator

from app.generators.testcase_generator import TestCaseGenerator


LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)


def main():

    with BrowserManager(headless=False) as browser:

        # -----------------------------
        # Login
        # -----------------------------
        login = LoginManager(
            browser=browser,
            login_url=LOGIN_URL,
        )

        login.ensure_login()

        # -----------------------------
        # Crawl Application
        # -----------------------------
        crawler = Crawler(browser.page)

        exploration_data = crawler.crawl()

        # -----------------------------
        # Save Exploration
        # -----------------------------
        print("Saving Exploration...")

        JsonExporter().export(
            exploration_data
        )

        print("Exploration completed.")

        # -----------------------------
        # Knowledge Builder
        # -----------------------------
        print("Building Knowledge...")

        knowledge = KnowledgeBuilder(
            exploration_data
        ).build()

        KnowledgeExporter().export(
            knowledge
        )

        # -----------------------------
        # Requirement Analyzer
        # -----------------------------
        print("Analyzing Requirements...")

        requirements = RequirementAnalyzer(
            knowledge
        ).analyze()

        RequirementsExporter().export(
            requirements
        )

        # -----------------------------
        # Feature Splitter
        # -----------------------------
        print("Splitting Features...")

        features = FeatureSplitter(
            requirements
        ).split()

        FeaturesExporter().export(
            features
        )

        # -----------------------------
        # Scenario Generator
        # -----------------------------
        print("Generating Scenarios...")

        scenarios = ScenarioGenerator(
            features
        ).generate()

        ScenariosExporter().export(
            scenarios
        )

        # -----------------------------
        # Test Case Generator
        # -----------------------------
        print("Generating Test Cases...")

        testcases = TestCaseGenerator(
            knowledge=knowledge,
            scenarios=scenarios
        ).generate()

        TestCaseExporter().export(
            testcases
        )

        # -----------------------------
        # Finished
        # -----------------------------
        print("\n" + "=" * 60)
        print("QA Web Agent finished successfully.")
        print("=" * 60)

        input("\nPress ENTER to close...")


if __name__ == "__main__":
    main()