import json
from pathlib import Path


class FeaturesExporter:

    def export(self, data):

        output = Path(
            "storage/features"
        )

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        file = output / "features.json"

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
            f"Features saved to: {file}"
        )