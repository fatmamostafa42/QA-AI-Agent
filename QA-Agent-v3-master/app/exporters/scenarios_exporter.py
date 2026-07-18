import json
from pathlib import Path


class ScenariosExporter:

    OUTPUT = Path("storage/scenarios/scenarios.json")

    def export(self, data):

        self.OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.OUTPUT,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Scenarios saved to: {self.OUTPUT}"
        )