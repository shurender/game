"""Player wallet — single source of truth for coins."""
from __future__ import annotations


class Wallet:
    """Singleton holding the player's coin total."""

    _instance: "Wallet | None" = None

    @classmethod
    def get_instance(cls) -> "Wallet":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, starting_coins: int = 3000) -> None:
        self.coins = starting_coins

    @property
    def _dict(self) -> dict[str, int]:
        """Dict view consumed by ShopTransaction without exposing internals."""
        return self.__dict__   # {"coins": int, …}  — ShopTransaction writes .coins directly

    def to_dict(self) -> dict[str, int]:
        return {"coins": self.coins}

    def load_dict(self, data: dict[str, int]) -> None:
        self.coins = data.get("coins", 0)

    def reset(self, coins: int = 3000) -> None:
        self.coins = coins
