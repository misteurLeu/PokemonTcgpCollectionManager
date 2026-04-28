import json
import numbers
import os

from parameters import DATA_PATH, RARITY_FILE, COLLECTION_FILE, USERS_DIRECTORY
from .decorators import log_function, require_data, test_dependency


class DataChecker:

    def __init__(self):
        self.rarity = None
        self.collections = None
        self.test_list = []

        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(DATA_PATH)
        if not os.path.exists(USERS_DIRECTORY):
            raise FileNotFoundError(USERS_DIRECTORY)
        if not os.path.exists(RARITY_FILE):
            raise FileNotFoundError(f"The json file for describing rarity does not exists under {RARITY_FILE} path")
        if not os.path.exists(COLLECTION_FILE):
            raise FileNotFoundError(f'The json file for describing collection'
                                    f' does not exists under {COLLECTION_FILE} path')

    @log_function
    def load_rarity(self):
        with open(RARITY_FILE, 'r') as f:
            self.rarity = json.load(f)
            if type(self.rarity) is not list:
                raise TypeError(RARITY_FILE)
            if len(self.rarity) == 0:
                raise Exception('No rarity data')

    @log_function
    def load_collections(self):
        with open(COLLECTION_FILE, 'r') as f:
            self.collections = json.load(f)
            if type(self.collections) is not list:
                raise TypeError(COLLECTION_FILE)
            if len(self.collections) == 0:
                raise Exception('No collections data')

    @log_function
    @require_data('rarity')
    @test_dependency()
    def check_rarity_structure(self):
        for i, rare in enumerate(self.rarity):
            if 'id' not in rare:
                raise ValueError(f'Missing id for rarity at index {i}')
            if not isinstance(rare['id'], int):
                raise TypeError(f'id in rarity must be an integer at index {i}')
            if 'name' not in rare:
                raise ValueError(f'Missing name for rarity at index {i}')
            if not isinstance(rare['name'], str):
                raise TypeError(f'name in rarity must be a string at index {i}')
            if 'desc' not in rare:
                raise ValueError(f'Missing description for rarity at index {i}')
            if not isinstance(rare['desc'], str):
                raise TypeError(f'description in rarity must be a string at index {i}')

    @log_function
    @require_data('rarity')
    @test_dependency('check_rarity_structure')
    def check_rarity_unicity(self):
        """Check rarity ids unicity"""
        rarity_ids = [item["id"] for item in self.rarity]
        if len(rarity_ids) != len(set(rarity_ids)):
            error_msg = "ids are not unique in rarity file, Please correct the datas\n"
            for rarity_id in set(rarity_ids):
                duplicated_times = rarity_ids.count(rarity_id)
                if duplicated_times > 1:
                    error_msg += f"    id {rarity_id}: is duplicated {duplicated_times} times\n"
            raise ValueError(error_msg)

    @log_function
    def check_rarity(self):
        """perform all checks on rarity datas"""
        self.check_rarity_structure()
        self.check_rarity_unicity()

    @log_function
    @require_data('collections')
    def check_collections_structure(self):
        for i, collection in enumerate(self.collections):
            if 'name' not in collection:
                raise ValueError(f'Missing name in collection {i}')
            if not isinstance(collection['name'], str):
                raise TypeError(f'name in collection should be a string')
            if 'boosters' not in collection:
                raise ValueError(f'Missing booster in collection {i}')
            if not isinstance(collection['boosters'], list):
                raise TypeError(f'boosters in collection should be a list')
            if len(collection['boosters']) == 0:
                raise ValueError(f'boosters in collection should not be empty')
            if 'cards' not in collection:
                raise ValueError(f'Missing card list in collection {i}')
            if not isinstance(collection['cards'], list):
                raise TypeError(f'cards in collection should be a list')
            if len(collection['cards']) == 0:
                raise ValueError(f'cards in collection should not be empty')

    @log_function
    @require_data('collections')
    @test_dependency('check_collections_structure')
    def check_collections_unicity(self):
        """check collections unicity"""
        collections_names = [collection['name'] for collection in self.collections]
        if len(set(collections_names)) != len(collections_names):
            error_msg = f"collection names are not unique in collections file, Please correct the datas\n"
            for collection_name in set(collections_names):
                duplicated_times = collections_names.count(collection_name)
                if duplicated_times > 1:
                    error_msg += "    name {collection_name}: is duplicated {duplicated_times} times\n"

    @log_function
    @require_data('collections')
    @test_dependency('check_collections_structure')
    def check_boosters_structure(self):
        for collection in self.collections:
            for i, booster in enumerate(collection['boosters']):
                if 'name' not in booster:
                    raise ValueError(f'Missing field name for booster n°{i} in collection {collection["name"]}')
                if not isinstance(booster['name'], str):
                    raise TypeError(f'Wrong type for field name in booster n°{i} in collection {collection["name"]}'
                                    f'should be a string, find a {type(booster["name"])}')
                if 'rarities' not in booster:
                    raise ValueError(f'Missing field rarities for booster n°{i} in collection {collection["name"]}')
                if not isinstance(booster['rarities'], list):
                    raise TypeError(f'Wrong type for field rarities in booster n°{i} in collection {collection["name"]}'
                                    f'should be a list, find a {type(booster["rarities"])}')

    @log_function
    @require_data('collections')
    @test_dependency('check_boosters_structure')
    def check_boosters_unicity(self):
        error_msg = ""
        for collection in self.collections:
            booster_names = [booster['name'] for booster in collection['boosters']]
            if len(set(booster_names)) == len(booster_names):
                continue
            error_msg += (f"boosters names are not unique in collection {collection['name']},"
                          f" Please correct the datas\n")
            for booster_name in set(booster_names):
                duplicated_times = booster_names.count(booster_name)
                if duplicated_times > 1:
                    error_msg += f"    name {booster_name}: is duplicated {duplicated_times} times\n"
        if error_msg != "":
            raise ValueError(error_msg)

    @log_function
    @require_data('collections')
    @test_dependency('check_boosters_unicity')
    def check_boosters_rarity_structure(self):
        for collection in self.collections:
            for booster in collection['boosters']:
                for i, rarity in enumerate(booster['rarities']):
                    error_context = f"rarity n°{i} in collection {collection['name']}>boosters>{booster['name']}"
                    if 'name' not in rarity:
                        raise ValueError(f"missing field name for {error_context}")
                    if not isinstance(rarity['name'], str):
                        raise TypeError(f"wrong type for field name in {error_context}"
                                        f" should be str, find {type(rarity['name'])}")
                    if 'rate' not in rarity:
                        raise ValueError(f"missing field rate for {error_context}")
                    if not isinstance(rarity['rate'], (float, int)):
                        raise TypeError(f"wrong type for field rate in {error_context}"
                                        f" should be float or int but found {type(rarity['rate'])}")
                    if rarity['rate'] < 0 or rarity['rate'] > 1:
                        raise ValueError(f"Rate should be between 0 and 1 included"
                                         f" {rarity['rate']} found in {error_context}")
                    if 'cardDrops' not in rarity:
                        raise ValueError(f"missing field cardDrops for {error_context}")
                    if not isinstance(rarity['cardDrops'], list):
                        raise TypeError(f"wrong type for field cardDrops in {error_context}"
                                        f" should be list, find {type(rarity['cardDrop'])}")

    @log_function
    @require_data('collections')
    @test_dependency('check_boosters_rarity_structure')
    def check_boosters_rarity_coherency(self):
        error_value = ""
        for collection in self.collections:
            for booster in collection['boosters']:
                error_context = f" for {booster['name']} in {collection['name']}"
                # rarities rate sum
                rarity_sum = sum([rarity['rate'] for rarity in booster['rarities']])
                if rarity_sum != 1:
                    error_value += f"rarity rate sum should be equal to 1, currently {rarity_sum} {error_context}\n"
                #rarities unicity
                rarity_names = [rarity['name'] for rarity in booster['rarities']]
                if len(rarity_names) != len(set(rarity_names)):
                    for rarity_name in set(rarity_names):
                        repeat_time = rarity_names.count(rarity_name)
                        if repeat_time > 1:
                            error_value += f"rarity {rarity_name} is repeated {repeat_time} times {error_context}\n"
        if error_value != "":
            raise ValueError(error_value)


    @log_function
    @require_data('collections')
    @test_dependency('check_boosters_rarity_coherency')
    def check_rarity_drops_structure(self):
        for collection in self.collections:
            for booster in collection['boosters']:
                for rarity in booster['rarities']:
                    for i, drop in enumerate(rarity['cardDrops']):
                        error_context = (f" for drop n°{i} in collection:"
                                         f" {collection['name']}>boosters>{booster['name']}>rarities>{rarity['name']}")
                        if "num_card" not in drop:
                            raise ValueError(f"Missing value num_card {error_context}")
                        if not isinstance(drop['num_card'], int):
                            raise TypeError(f"Value num_card should be an integer,"
                                            f" currently {type(drop['num_card'])} {error_context}")
                        if "dropRates" not in drop:
                            raise ValueError(f"Missing value cardDrops {error_context}")
                        if not isinstance(drop['dropRates'], list):
                            raise TypeError(f"Value dropRates should be a list,"
                                            f" currently {type(drop['dropRates'])} {error_context}")

    @log_function
    @require_data('collections')
    @test_dependency('check_rarity_drops_structure')
    def check_rarity_drops_coherency(self):
        for collection in self.collections:
            for booster in collection['boosters']:
                for rarity in booster['rarities']:
                    error_context = f" in {collection['name']}>boosters>{booster['name']}>rarities>{rarity['name']}"
                    nums_card = [drop['num_card'] for drop in rarity['cardDrops']]
                    set_cards = list(set(nums_card))
                    if len(nums_card) != len(set_cards):
                        raise ValueError(f"card drops ids should be uniques {error_context}")
                    if not set_cards[0] == 1 or not all([i + 1 == j for i, j in zip(set_cards, set_cards[1:])]):
                        raise ValueError(f"drops card num should start with 1 "
                                         f"and be consecutive numbers {error_context}")

    @log_function
    @require_data('collections')
    @test_dependency('check_rarity_drops_coherency')
    def check_drops_rate_structure(self):
        for collection in self.collections:
            for booster in collection['boosters']:
                for rarity in booster['rarities']:
                    for drop in rarity['cardDrops']:
                        for i, rate in enumerate(drop['dropRates']):
                            error_context = (f"for rate n°{i} in {collection['name']}>"
                                             f"boosters>{booster['name']}>rarities>{rarity['name']}>")
                            if 'rarity' not in rate:
                                raise ValueError(f"Missing value rarity {error_context}")
                            if not isinstance(rate['rarity'], int):
                                raise TypeError(f"Rarity should be an integer,"
                                                f" not {type(rate['rarity'])} {error_context}")
                            if 'rate' not in rate:
                                raise ValueError(f"Missing value drop {error_context}")
                            if not isinstance(rate['rate'], (int, float)):
                                raise TypeError(f"rate should be an integer or a float,"
                                                f" not {type(rate['rate'])} {error_context}")

    @log_function
    @require_data('collections', 'rarity')
    @test_dependency('check_drops_rate_structure', 'check_rarity_unicity')
    def check_drops_rate_coherency(self):
        rarities_ids = [rare['id'] for rare in self.rarity]
        for collection in self.collections:
            for booster in collection['boosters']:
                for rarity in booster['rarities']:
                    for drop in rarity['cardDrops']:
                        error_context = (f"in {collection['name']}>boosters>"
                                         f"{booster['name']}>rarities>{rarity['name']}>cardDrops>{drop['num_card']}")
                        rate_sum = sum([dropRate['rate'] for dropRate in drop['dropRates']])
                        if rate_sum != 1:
                            raise ValueError(f"rates sum should be 1, not {rate_sum} {error_context}")
                        rate_rarity = [drop_rate['rarity'] for drop_rate in drop['dropRates']]
                        rate_rarity_set = list(set(rate_rarity))
                        if len(rate_rarity) != len(rate_rarity_set):
                            raise ValueError(f"duplicate rarity {error_context}")
                        if not all([rarity_item in rarities_ids for rarity_item in rate_rarity_set]):
                            raise ValueError(f"some rarities does not exist in rarity table {error_context}")

    @log_function
    @require_data('collections')
    @test_dependency('check_collections_unicity')
    def check_collection_cards_structure(self):
        for collection in self.collections:
            for i, card in enumerate(collection['cards']):
                error_context = f"for card {i} in collection {collection['name']}"
                if 'idPokedex' not in card:
                    raise ValueError(f"missing value idPokedex {error_context}")
                if not isinstance(card['idPokedex'], int):
                    raise TypeError(f"idPokedex should be an integer, not {type(card['idPokedex'])} {error_context}")
                if 'idCollection' not in card:
                    raise ValueError(f"missing value idCollection {error_context}")
                if not isinstance(card['idCollection'], int):
                    raise TypeError(f"idCollection should be an integer,"
                                    f" not {type(card['idCollection'])} {error_context}")
                if 'name' not in card:
                    raise ValueError(f"missing value name {error_context}")
                if not isinstance(card['name'], str):
                    raise TypeError(f"name should be a string, not {type(card['name'])} {error_context}")
                if 'rarity' not in card:
                    raise ValueError(f"missing value rarity {error_context}")
                if not isinstance(card['rarity'], int):
                    raise TypeError(f"rarity should be an integer, not {type(card['rarity'])} {error_context}")
                if 'boosters' not in card:
                    raise ValueError(f"missing value boosters {error_context}")
                if not isinstance(card['boosters'], list):
                    raise TypeError(f"boosters should be a list, not {type(card['boosters'])} {error_context}")

    @log_function
    @require_data('collections', 'rarity')
    @test_dependency('check_boosters_unicity', 'check_rarity_unicity')
    def check_collection_card_coherency(self):
        rarities_id = [rare['id'] for rare in self.rarity]
        for collection in self.collections:
            ids_collection = [card['idCollection'] for card in collection['cards']]
            ids_collection_set = list(set(ids_collection))
            if len(ids_collection) != len(ids_collection_set):
                err_mess = f"cards in collection {collection['name']} have duplicated idCollection\n"
                for id_coll in ids_collection_set:
                    count_id = ids_collection.count(id_coll)
                    if count_id > 1:
                        err_mess += f"idCollecion: {id_coll} is duplicated {count_id} times\n"
                raise ValueError(err_mess)
            err_mess = ""
            for i, j in zip(ids_collection_set, ids_collection_set[1:]):
                if i + 1 != j:
                    err_mess += f"card idCollection: {i} and {j} are not consecutive in {collection['name']}\n"
            if err_mess != "":
                raise ValueError(err_mess)

            boosters_names = [booster['name'] for booster in collection['boosters']]
            err_mess = ""
            for card in collection['cards']:
                error_context = f"for card idCollection {card['idCollection']} in collection {collection['name']}"
                if card['rarity'] not in rarities_id:
                    err_mess += f"rarity {card['rarity']} does not exists in rarities {error_context}\n"
                if len(card['boosters']) == 0:
                    err_mess += f"no boosters found {error_context}\n"
                if len(card['boosters']) != len(set(card['boosters'])):
                    err_mess += f"duplicated boosters {error_context}\n"
                if not all([booster_name in boosters_names for booster_name in card['boosters']]):
                    err_mess += f"some boosters does not exists in collection boosters {error_context}\n"

            if err_mess != "":
                raise ValueError(err_mess)

    def check_collections(self):
        """Perform all checks on collections"""
        self.check_collections_structure()
        self.check_collections_unicity()
        self.check_boosters_structure()
        self.check_boosters_unicity()
        self.check_boosters_rarity_structure()
        self.check_boosters_rarity_coherency()
        self.check_rarity_drops_structure()
        self.check_rarity_drops_coherency()
        self.check_drops_rate_structure()
        self.check_drops_rate_coherency()
        self.check_collection_cards_structure()
        self.check_collection_card_coherency()

    def run(self):
        self.check_rarity()
        self.check_collections()
