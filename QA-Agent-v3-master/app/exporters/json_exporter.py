import json
from pathlib import Path


class JsonExporter:
    """
    Export exploration data to a JSON file.
    """

    def __init__(self, output_dir: str = "storage/exploration"):

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        data: dict,
        filename: str = "exploration.json",
    ) -> Path:

        output_file = self.output_dir / filename

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Exploration saved to: {output_file}")

        return output_file