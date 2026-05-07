import json
import unicodedata

from input import RARITY_FILE
from dataclasses import dataclass


@dataclass
class Rarity:
    id: int
    name: str
    desc: str

    def __str__(self):
        return f"id: {self.id} name: {self.name}, desc: {self.desc}"

    @classmethod
    def load_rarity(cls) -> list["Rarity"]:
        with open(RARITY_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            rarities = []
            for item in data:
                rarities.append(Rarity(
                    id=item["id"],
                    name=item["name"],
                    desc=item["desc"]))
        return rarities
