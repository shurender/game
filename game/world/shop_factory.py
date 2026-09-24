"""Loads Shop objects from shops.json."""
from __future__ import annotations

from game.world.shop import Shop, ShopListing
from game.inventory.item_factory import ItemFactory
from game.utils.data_loader import load_json_file


class ShopFactory:
    """Singleton that loads shops.json and constructs Shop objects."""

    _instance: "ShopFactory | None" = None

    @classmethod
    def get_instance(cls) -> "ShopFactory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        data = load_json_file("shops.json")
        item_factory = ItemFactory.get_instance()

        self._shops: dict[str, Shop] = {}
        for shop_id, d in data.get("shops", {}).items():
            listings: list[ShopListing] = []
            for item_id in d.get("sells", []):
                try:
                    item = item_factory.get(item_id)
                    listings.append(ShopListing(item=item, buy_price=item.price))
                except ValueError:
                    pass   # Unknown item — skip gracefully

            self._shops[shop_id] = Shop(
                shop_id=shop_id,
                name=d["name"],
                greeting=d.get("greeting", "Welcome!"),
                farewell=d.get("farewell", "Goodbye!"),
                listings=listings,
                buys_items=d.get("buys", True),
                sell_rate=d.get("sell_rate", 0.5),
            )

    def get(self, shop_id: str) -> Shop:
        shop = self._shops.get(shop_id)
        if shop is None:
            raise ValueError(f"Unknown shop ID: {shop_id}")
        return shop

    def all(self) -> list[Shop]:
        return list(self._shops.values())
