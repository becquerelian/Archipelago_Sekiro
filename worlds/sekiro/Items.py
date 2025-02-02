# Adapted from the DS3 world code

## IMPORTS ##

from dataclasses import dataclass
import dataclasses
from enum import IntEnum
from typing import Any, cast, ClassVar, Dict, Generator, List, Optional, Set

from BaseClasses import Item, ItemClassification


## CATEGORIES ##

class SekiroItemCategory(IntEnum):
    MISC = 0
    UNIQUE = 1
    BOSS = 2
    SEN = 3
    HEALING = 4
    SKILLS = 5


## DATA CLASSES ##

@dataclass
class SekiroItemData:
    __item_id: ClassVar[int] = 100000
    """The next item ID to use when creating item data."""

    name: str
    sekiro_code: Optional[int]
    category: SekiroItemCategory


    base_name: Optional[str] = None
    """The name of the individual item, if this is a multi-item group."""

    classification: ItemClassification = ItemClassification.filler
    """How important this item is to the game progression."""

    ap_code: Optional[int] = None
    """The Archipelago ID for this item."""

    count: int = 1
    """The number of copies of this item included in each drop."""

    inject: bool = False
    """If this is set, the randomizer will try to inject this item into the game.

    This is used for items such as covenant rewards that aren't realistically reachable in a
    randomizer run, but are still fun to have available to the player. If there are more locations
    available than there are items in the item pool, these items will be used to help make up the
    difference.
    """

    sen: Optional[int] = None
    """If this is a consumable item that gives sen, the amount of sen it gives."""

    filler: bool = False
    """Whether this is a candidate for a filler item to be added to fill out extra locations."""

    skip: bool = False
    """Whether to omit this item from randomization and replace it with filler or unique items."""

    @property
    def unique(self):
        """Whether this item should be unique, appearing only once in the randomizer."""
        return self.category not in {
            SekiroItemCategory.SKILLS, SekiroItemCategory.BOSS, SekiroItemCategory.UNIQUE,
            SekiroItemCategory.HEALING, 
        }

    def __post_init__(self):
        self.ap_code = self.ap_code or SekiroItemData.__item_id
        if not self.base_name: self.base_name = self.name
        if not self.base_sekiro_code: self.base_sekiro_code = self.sekiro_code
        SekiroItemData.__item_id += 1

    def item_groups(self) -> List[str]:
        """The names of item groups this item should appear in.

        This is computed from the properties assigned to this item."""
        names = []
        if self.classification == ItemClassification.progression: names.append("Progression")

        names.append({
            SekiroItemCategory.MISC: "Miscellaneous",
            SekiroItemCategory.UNIQUE: "Unique",
            SekiroItemCategory.BOSS: "Boss Memories",
            SekiroItemCategory.SEN: "Sen",
            SekiroItemCategory.SKILLS: "Skill Tree",
            SekiroItemCategory.HEALING: "Healing",
        }[self.category])

        return names

    def counts(self, counts: List[int]) -> Generator["SekiroItemData", None, None]:
        """Returns an iterable of copies of this item with the given counts."""
        yield self
        for count in counts:
            yield dataclasses.replace(
                self,
                ap_code = None,
                name = "{} x{}".format(self.base_name, count),
                base_name = self.base_name,
                count = count,
                filler = False, # Don't count multiples as filler by default
            )


class SekiroItem(Item):
    game: str = "Sekiro: Shadows Die Twice"
    data: SekiroItemData

    def __init__(
            self,
            player: int,
            data: SekiroItemData,
            classification = None):
        super().__init__(data.name, classification or data.classification, data.ap_code, player)
        self.data = data

    @staticmethod
    def event(name: str, player: int) -> "SekiroItem":
        data = SekiroItemData(name, None, SekiroItemCategory.MISC,
                           skip = True, classification = ItemClassification.progression)
        data.ap_code = None
        return SekiroItem(player, data)


## ITEM LIST ##

_all_items = [

]

item_name_groups: Dict[str, Set] = {
    "Progression": set(),
    "Prosthetics": set(),
    "Miscellaneous": set(),
    "Unique": set(),
    "Boss Memories": set(),
    "Sen": set(),
    "Skills": set(),
    "Healing": set(),
}


## ORGANIZATION ##

item_descriptions = {
    "Progression": "Items which unlock locations.",
    "Prosthetics": "Items which unlock locations.",
    "Miscellaneous": "Items which unlock locations.",
    "Unique": "Items which unlock locations.",
    "Boss Memories": "Items which unlock locations.",
    "Sen": "Items which unlock locations.",
    "Skills": "Items which unlock locations.",
    "Healing": "Items which unlock locations.",
}

for item_data in _all_items:
    for group_name in item_data.item_groups():
        item_name_groups[group_name].add(item_data.name)

filler_item_names = [item_data.name for item_data in _all_items if item_data.filler]
item_dictionary = {item_data.name: item_data for item_data in _all_items}