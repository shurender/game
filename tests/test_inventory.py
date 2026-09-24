"""Tests for the inventory system."""
import pytest
from unittest.mock import patch

from game.inventory.item import Item
from game.inventory.item_factory import ItemFactory
from game.inventory.inventory import Inventory
from game.inventory.healing_item import use_healing_item
from game.inventory.battle_item import use_battle_item
from game.creatures.creature import Creature, Species
from game.battle.status_effects import StatusEffect
from game.player.party import PartyManager


# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_ITEMS = {
    "items": {
        "I1": {"name": "Health Vial",    "category": "Healing",   "effect": "heal_hp",     "value": 20,     "price": 100, "description": "Heals 20 HP."},
        "I2": {"name": "Antidote Balm",  "category": "Healing",   "effect": "cure_status", "value": "Poison","price": 150, "description": "Cures Poison."},
        "I3": {"name": "Capture Sphere", "category": "Capture",   "effect": "capture",     "value": 1.0,    "price": 200, "description": "Catches creatures."},
        "I4": {"name": "Energy Drink",   "category": "Stat Boost","effect": "boost_spd",   "value": 1,      "price": 500, "description": "Boosts Speed."},
        "I5": {"name": "Old Map",        "category": "Key Item",  "effect": "none",         "value": 0,     "price": 0,   "description": "A map."},
    }
}


@pytest.fixture(autouse=True)
def reset_singletons():
    """Fresh singletons before each test."""
    ItemFactory._instance = None
    Inventory._instance = None
    PartyManager._instance = None
    with patch("game.inventory.item_factory.load_json_file", return_value=MOCK_ITEMS):
        yield
    ItemFactory._instance = None
    Inventory._instance = None
    PartyManager._instance = None


@pytest.fixture
def inv():
    return Inventory.get_instance()


@pytest.fixture
def species():
    return Species(
        "t", "TestMon", ["Normal"],
        {"hp": 100, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        "Test"
    )


@pytest.fixture
def creature(species):
    c = Creature(species, level=5)
    c.current_hp = 40   # damaged
    return c


# ── ItemFactory ───────────────────────────────────────────────────────────────

def test_item_factory_loads_items():
    factory = ItemFactory.get_instance()
    item = factory.get("I1")
    assert item.name == "Health Vial"
    assert item.category == "Healing"
    assert item.effect == "heal_hp"
    assert item.value == 20


def test_item_factory_category_filter():
    factory = ItemFactory.get_instance()
    healing = factory.by_category("Healing")
    assert all(i.category == "Healing" for i in healing)
    assert len(healing) == 2


def test_item_factory_unknown_raises():
    factory = ItemFactory.get_instance()
    with pytest.raises(ValueError):
        factory.get("NOPE")


# ── Inventory quantities ──────────────────────────────────────────────────────

def test_add_and_quantity(inv):
    inv.add("I1", 3)
    assert inv.quantity("I1") == 3

def test_add_increases_existing(inv):
    inv.add("I1", 2)
    inv.add("I1", 1)
    assert inv.quantity("I1") == 3

def test_remove_decrements(inv):
    inv.add("I1", 5)
    inv.remove("I1", 2)
    assert inv.quantity("I1") == 3

def test_remove_to_zero_cleans_up(inv):
    inv.add("I1", 1)
    inv.remove("I1", 1)
    assert inv.quantity("I1") == 0
    assert not inv.has("I1")

def test_remove_insufficient_raises(inv):
    inv.add("I1", 1)
    with pytest.raises(ValueError):
        inv.remove("I1", 2)

def test_add_invalid_item_raises(inv):
    with pytest.raises(ValueError):
        inv.add("BOGUS")


# ── Category filtering ────────────────────────────────────────────────────────

def test_by_category(inv):
    inv.add("I1", 1)
    inv.add("I3", 2)
    inv.add("I4", 1)
    healing = inv.by_category("Healing")
    assert len(healing) == 1
    assert healing[0][0].item_id == "I1"


# ── Healing item logic ────────────────────────────────────────────────────────

def test_heal_hp(creature):
    item = ItemFactory.get_instance().get("I1")   # +20 HP
    half_hp = creature.stats.hp // 2
    creature.current_hp = half_hp
    before = creature.current_hp
    msg = use_healing_item(item, creature)
    expected = min(creature.stats.hp, before + 20)
    assert creature.current_hp == expected
    assert "recovered" in msg

def test_heal_hp_caps_at_max(creature):
    item = ItemFactory.get_instance().get("I1")
    creature.current_hp = creature.stats.hp - 5
    use_healing_item(item, creature)
    assert creature.current_hp == creature.stats.hp

def test_heal_fainted_raises(creature):
    item = ItemFactory.get_instance().get("I1")
    creature.current_hp = 0
    with pytest.raises(ValueError, match="fainted"):
        use_healing_item(item, creature)

def test_cure_status_success(creature):
    item = ItemFactory.get_instance().get("I2")   # cures Poison
    creature.status = StatusEffect.POISON
    msg = use_healing_item(item, creature)
    assert creature.status == StatusEffect.NONE
    assert "cured" in msg.lower()

def test_cure_status_wrong_status_raises(creature):
    item = ItemFactory.get_instance().get("I2")   # cures Poison only
    creature.status = StatusEffect.BURN
    with pytest.raises(ValueError):
        use_healing_item(item, creature)

def test_cure_status_none_raises(creature):
    item = ItemFactory.get_instance().get("I2")
    with pytest.raises(ValueError):
        use_healing_item(item, creature)


# ── Inventory.use dispatch ────────────────────────────────────────────────────

def test_use_healing_via_inventory(inv, creature):
    inv.add("I1", 2)
    msg = inv.use("I1", target=creature)
    assert "recovered" in msg
    assert inv.quantity("I1") == 1   # consumed one

def test_use_with_no_stock_raises(inv, creature):
    with pytest.raises(ValueError, match="no"):
        inv.use("I1", target=creature)

def test_use_key_item_raises(inv):
    inv.add("I5", 1)
    with pytest.raises(ValueError, match="key item"):
        inv.use("I5")

def test_use_requires_target_for_healing(inv):
    inv.add("I1", 1)
    with pytest.raises(ValueError, match="target"):
        inv.use("I1")


# ── Battle item (stat boost) ──────────────────────────────────────────────────

def test_battle_item_boosts_stat(creature):
    item = ItemFactory.get_instance().get("I4")   # boost_spd
    before = creature.stats.spd
    msg = use_battle_item(item, creature)
    assert creature.stats.spd > before
    assert "Speed" in msg

def test_battle_item_via_inventory(inv, creature):
    inv.add("I4", 1)
    msg = inv.use("I4", target=creature)
    assert inv.quantity("I4") == 0
    assert "Speed" in msg


# ── Serialisation ─────────────────────────────────────────────────────────────

def test_to_and_from_dict(inv):
    inv.add("I1", 3)
    inv.add("I4", 1)
    data = inv.to_dict()
    assert data == {"I1": 3, "I4": 1}

    Inventory._instance = None
    inv2 = Inventory.get_instance()
    inv2.load_dict(data)
    assert inv2.quantity("I1") == 3
    assert inv2.quantity("I4") == 1
