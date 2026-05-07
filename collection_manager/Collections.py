import json
import os
import unicodedata

from input import COLLECTION_PATH
from dataclasses import dataclass
from typing import List


@dataclass
class DropRate:
    rarity: int
    rate: int

    @classmethod
    def import_from_dict(cls, data: dict) -> "DropRate":
        """Import DropRate data from dictionary"""
        return DropRate(rarity=data['rarity'], rate=data['rate'])


@dataclass
class CardDrops:
    num_card: int
    dropRates: List[DropRate]

    @classmethod
    def import_from_dict(cls, data: dict) -> "CardDrops":
        """Import CardDrops data from dictionary"""
        return CardDrops(
            num_card=data['num_card'],
            dropRates=[DropRate.import_from_dict(drop_rate) for drop_rate in data['dropRates']],
        )


@dataclass
class RarityDrops:
    name: str
    rate: float
    card_drops: List[CardDrops]

    @classmethod
    def import_from_dict(cls, data: dict) -> "RarityDrops":
        """Import RarityDrops data from dictionary"""
        return RarityDrops(
            name=data['name'],
            rate=data['rate'],
            card_drops=[CardDrops.import_from_dict(drop) for drop in data['cardDrops']],
        )


@dataclass
class Booster:
    name: str
    rarities: List[RarityDrops]

    @classmethod
    def import_from_dict(cls, data: dict) -> "Booster":
        """Import booster data from dictionary"""
        return Booster(
            name=data['name'],
            rarities=[RarityDrops.import_from_dict(rarity) for rarity in data['rarities']],
        )


@dataclass
class Card:
    id_pokedex: int
    id_collection: int
    name: str
    rarity: int
    boosters: List[str]

    @classmethod
    def import_from_dict(cls, data: dict) -> "Card":
        """Import Card data from dictionary"""
        return Card(
            id_pokedex=data['idPokedex'],
            id_collection=data['idCollection'],
            name=data['name'],
            rarity=data['rarity'],
            boosters=data['boosters'],
        )


@dataclass
class Collection:
    name: str
    boosters: List[Booster]
    cards: List[Card]

    @classmethod
    def import_from_json_file(cls, path: str) -> "Collection":
        """Import collection data from collections file"""
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
            return Collection(
                name=data['name'],
                boosters=[Booster.import_from_dict(booster) for booster in data['boosters']],
                cards=[Card.import_from_dict(card) for card in data['cards']],
            )

    @classmethod
    def import_all_from_collection_dir(cls) -> List["Collection"]:
        """Import all collections under collection directory"""
        collections = []
        for filename in os.listdir(COLLECTION_PATH):
            if filename == '.' or filename == '..':
                continue
            collection = Collection.import_from_json_file(os.path.join(COLLECTION_PATH, filename))
            collections.append(collection)
        return collections
