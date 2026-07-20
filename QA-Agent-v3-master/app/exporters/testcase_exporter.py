import json
from pathlib import Path


class TestCaseExporter:

    def export(self, testcases):

        output = Path("storage/testcases")
        output.mkdir(parents=True, exist_ok=True)

        file = output / "testcases.json"

        with open(
            file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                testcases,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Test Cases saved to: {file}")