import json
from pathlib import Path


class KnowledgeExporter:

    OUTPUT = Path("storage/knowledge")

    def export(self, knowledge):

        self.OUTPUT.mkdir(
            parents=True,
            exist_ok=True
        )

        output = self.OUTPUT / "knowledge.json"

        with open(
            output,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                knowledge,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Knowledge saved to: {output}"
        )