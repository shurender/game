"""Tests for shop logic — no Pygame, no UI."""
import pytest
from unittest.mock import patch

from game.world.shop import Shop, ShopListing, ShopTransaction, InsufficientFundsError
from game.world.shop_factory import ShopFactory
from game.inventory.inventory import Inventory
from game.inventory.item import Item
from game.inventory.item_factory import ItemFactory
from game.player.wallet import Wallet


# ── Mock data ────────────────────────────────────────────────────────────────

MOCK_ITEMS = {
    "items": {
        "I1": {"name": "Health Vial",    "category": "Healing",  "effect": "heal_hp",
               "value": 20, "price": 100, "description": "Heals 20 HP."},
        "I3": {"name": "Capture Sphere", "category": "Capture",  "effect": "capture",
               "value": 1.0, "price": 200, "description": "Catches creatures."},
        "I8": {"name": "Old Map",        "category": "Key Item", "effect": "none",
               "value": 0,  "price": 0,   "description": "A map."},
    }
}

MOCK_SHOPS = {
    "shops": {
        "shop_test": {
            "name": "Test Shop",
            "greeting": "Hello!",
            "farewell": "Bye!",
            "sells": ["I1", "I3"],
            "buys": True,
            "sell_rate": 0.5,
        },
        "shop_no_buy": {
            "name": "Sell-only Shop",
            "greeting": "Looking to buy?",
            "farewell": "See ya!",
            "sells": ["I1"],
            "buys": False,
            "sell_rate": 0.0,
        },
    }
}


@pytest.fixture(autouse=True)
def reset_singletons():
    ItemFactory._instance = None
    ShopFactory._instance = None
    Inventory._instance = None
    Wallet._instance = None
    with patch("game.inventory.item_factory.load_json_file", return_value=MOCK_ITEMS):
        with patch("game.world.shop_factory.load_json_file", return_value=MOCK_SHOPS):
            yield
    ItemFactory._instance = None
    ShopFactory._instance = None
    Inventory._instance = None
    Wallet._instance = None


@pytest.fixture
def shop():
    return ShopFactory.get_instance().get("shop_test")


@pytest.fixture
def inv():
    return Inventory.get_instance()


@pytest.fixture
def wallet():
    w = Wallet.get_instance()
    w.reset(1000)
    return w


@pytest.fixture
def txn(shop, inv, wallet):
    return ShopTransaction(shop, inv, wallet.__dict__)


# ── ShopFactory ───────────────────────────────────────────────────────────────

def test_factory_loads_shop():
    s = ShopFactory.get_instance().get("shop_test")
    assert s.name == "Test Shop"
    assert s.greeting == "Hello!"
    assert len(s.listings) == 2


def test_factory_listings_have_correct_prices():
    s = ShopFactory.get_instance().get("shop_test")
    prices = {lst.item.item_id: lst.buy_price for lst in s.listings}
    assert prices["I1"] == 100   # item.price
    assert prices["I3"] == 200


def test_factory_unknown_shop_raises():
    with pytest.raises(ValueError):
        ShopFactory.get_instance().get("nonexistent")


# ── Buying ────────────────────────────────────────────────────────────────────

def test_buy_success(txn, inv, wallet):
    item = ItemFactory.get_instance().get("I1")
    msg = txn.buy(item)
    assert inv.quantity("I1") == 1
    assert wallet.coins == 900
    assert "Bought" in msg


def test_buy_multiple_qty(txn, inv, wallet):
    item = ItemFactory.get_instance().get("I1")
    txn.buy(item, qty=3)
    assert inv.quantity("I1") == 3
    assert wallet.coins == 700


def test_buy_insufficient_funds_raises(txn, wallet):
    wallet.reset(50)   # only 50 coins, item costs 100
    item = ItemFactory.get_instance().get("I1")
    with pytest.raises(InsufficientFundsError):
        txn.buy(item)


def test_buy_insufficient_funds_no_inventory_change(txn, inv, wallet):
    wallet.reset(50)
    item = ItemFactory.get_instance().get("I1")
    try:
        txn.buy(item)
    except InsufficientFundsError:
        pass
    assert inv.quantity("I1") == 0   # nothing added


def test_buy_item_not_in_shop_raises(txn):
    fake_item = Item("FAKE", "Fake", "Healing", "heal_hp", 0, 0, "")
    with pytest.raises(ValueError):
        txn.buy(fake_item)


def test_can_buy_returns_false_no_funds(txn, wallet):
    wallet.reset(0)
    item = ItemFactory.get_instance().get("I1")
    ok, reason = txn.can_buy(item)
    assert ok is False
    assert "enough" in reason.lower()


# ── Selling ───────────────────────────────────────────────────────────────────

def test_sell_success(txn, inv, wallet):
    inv.add("I1", 2)
    item = ItemFactory.get_instance().get("I1")
    msg = txn.sell(item)
    assert inv.quantity("I1") == 1
    assert wallet.coins == 1050  # 1000 + 50 (100 * 0.5)
    assert "Sold" in msg


def test_sell_multiple_qty(txn, inv, wallet):
    inv.add("I1", 5)
    item = ItemFactory.get_instance().get("I1")
    txn.sell(item, qty=3)
    assert inv.quantity("I1") == 2
    assert wallet.coins == 1150  # +150


def test_sell_key_item_raises(txn, inv):
    inv.add("I8", 1)
    item = ItemFactory.get_instance().get("I8")
    with pytest.raises(ValueError, match="[Kk]ey item"):
        txn.sell(item)


def test_sell_insufficient_qty_raises(txn):
    item = ItemFactory.get_instance().get("I1")
    with pytest.raises(ValueError):
        txn.sell(item, qty=5)   # don't own any


def test_sell_to_no_buy_shop_raises(inv):
    s = ShopFactory.get_instance().get("shop_no_buy")
    wallet = Wallet.get_instance()
    t = ShopTransaction(s, inv, wallet.__dict__)
    inv.add("I1", 1)
    item = ItemFactory.get_instance().get("I1")
    with pytest.raises(ValueError, match="doesn't buy"):
        t.sell(item)


# ── Sell price calculation ────────────────────────────────────────────────────

def test_sell_price_is_half_buy_price(shop):
    item = ItemFactory.get_instance().get("I1")
    assert shop.sell_price_for(item) == 50   # 100 * 0.5


def test_sell_price_minimum_one():
    free_item = Item("FREE", "Freebie", "Healing", "heal_hp", 0, 0, "")
    shop = Shop("s", "S", "Hi", "Bye", [], True, 0.5)
    assert shop.sell_price_for(free_item) == 1


# ── Wallet isolation ──────────────────────────────────────────────────────────

def test_wallet_not_mutated_on_failed_buy(txn, wallet):
    wallet.reset(50)
    item = ItemFactory.get_instance().get("I1")   # costs 100
    before = wallet.coins
    try:
        txn.buy(item)
    except InsufficientFundsError:
        pass
    assert wallet.coins == before
