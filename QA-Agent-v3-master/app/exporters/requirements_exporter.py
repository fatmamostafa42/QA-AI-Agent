import json
from pathlib import Path


class RequirementsExporter:

    def __init__(self):

        self.output = Path(
            "storage/requirements"
        )

        self.output.mkdir(
            parents=True,
            exist_ok=True
        )

    def export(self, data):

        file = self.output / "requirements.json"

        with open(
            file,
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
            f"Requirements saved to: {file}"
        )