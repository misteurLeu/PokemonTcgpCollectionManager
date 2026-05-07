from collection_manager.rarity import Rarity
from collection_manager.Collections import Collection

rarities = Rarity.load_rarity()
collection = Collection.import_all_from_collection_dir()

for rarity in rarities:
    print(rarity)
for collection in collection:
    print(collection)
