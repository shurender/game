"""Loads Item objects from items.json."""
from game.inventory.item import Item
from game.utils.data_loader import load_json_file


class ItemFactory:
    """Singleton that builds and caches Item definitions from JSON."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "ItemFactory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        data = load_json_file("items.json")
        raw = data.get("items", {})

        self._items: dict[str, Item] = {}
        for item_id, d in raw.items():
            self._items[item_id] = Item(
                item_id=item_id,
                name=d["name"],
                category=d["category"],
                effect=d["effect"],
                value=d.get("value", 0),
                price=d.get("price", 0),
                description=d.get("description", ""),
            )

    def get(self, item_id: str) -> Item:
        item = self._items.get(item_id)
        if item is None:
            raise ValueError(f"Unknown item ID: {item_id}")
        return item

    def all(self) -> list[Item]:
        return list(self._items.values())

    def by_category(self, category: str) -> list[Item]:
        return [i for i in self._items.values() if i.category == category]
