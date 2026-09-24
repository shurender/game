"""Shop domain model and pure transaction logic."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.inventory.item import Item


@dataclass
class ShopListing:
    """One purchasable row in a shop — item + its buy price."""
    item: "Item"
    buy_price: int          # Full price charged to player


@dataclass
class Shop:
    """Immutable shop definition; no UI, no state mutation beyond returning results.

    All write side-effects (money / inventory changes) are handled by ShopTransaction.
    """
    shop_id: str
    name: str
    greeting: str
    farewell: str
    listings: list[ShopListing] = field(default_factory=list)
    buys_items: bool = True
    sell_rate: float = 0.5   # fraction of buy price refunded on sell

    def sell_price_for(self, item: "Item") -> int:
        """Price the shop pays the player for a sold item."""
        return max(1, int(item.price * self.sell_rate))


class InsufficientFundsError(ValueError):
    pass


class ShopTransaction:
    """Executes buy/sell operations against an Inventory and a wallet.

    The wallet is represented by a mutable dict ``{"coins": int}`` so the
    caller's money object stays decoupled from shop internals.
    """

    def __init__(self, shop: Shop, inventory, wallet: dict[str, int]) -> None:
        self.shop = shop
        self.inventory = inventory
        self.wallet = wallet          # {"coins": int}

    # ── Buy ─────────────────────────────────────────────────────────────────

    def can_buy(self, item: "Item", qty: int = 1) -> tuple[bool, str]:
        """Return (ok, reason). reason is '' on success."""
        listing = self._listing_for(item)
        if listing is None:
            return False, f"{self.shop.name} doesn't sell {item.name}."
        total = listing.buy_price * qty
        if self.wallet["coins"] < total:
            return False, f"Not enough coins. Need {total}, have {self.wallet['coins']}."
        return True, ""

    def buy(self, item: "Item", qty: int = 1) -> str:
        """Deduct coins and add item to inventory.

        Returns a success message.
        Raises InsufficientFundsError or ValueError on bad input.
        """
        ok, reason = self.can_buy(item, qty)
        if not ok:
            if "enough" in reason.lower():
                raise InsufficientFundsError(reason)
            raise ValueError(reason)

        listing = self._listing_for(item)
        total = listing.buy_price * qty
        self.wallet["coins"] -= total
        self.inventory.add(item.item_id, qty)
        return f"Bought {qty}× {item.name} for {total} coins."

    # ── Sell ────────────────────────────────────────────────────────────────

    def can_sell(self, item: "Item", qty: int = 1) -> tuple[bool, str]:
        if not self.shop.buys_items:
            return False, f"{self.shop.name} doesn't buy items."
        if item.category == "Key Item":
            return False, f"Key items cannot be sold."
        if not self.inventory.has(item.item_id, qty):
            return False, f"You don't have {qty}× {item.name}."
        return True, ""

    def sell(self, item: "Item", qty: int = 1) -> str:
        """Remove item from inventory and credit coins.

        Returns a success message.
        Raises ValueError on bad input.
        """
        ok, reason = self.can_sell(item, qty)
        if not ok:
            raise ValueError(reason)

        payout = self.shop.sell_price_for(item) * qty
        self.inventory.remove(item.item_id, qty)
        self.wallet["coins"] += payout
        return f"Sold {qty}× {item.name} for {payout} coins."

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _listing_for(self, item: "Item") -> ShopListing | None:
        for listing in self.shop.listings:
            if listing.item.item_id == item.item_id:
                return listing
        return None
