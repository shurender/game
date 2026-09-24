"""ShopNPC — an NPC that opens a shop instead of dialogue."""
from __future__ import annotations

from game.world.npc import NPC
from game.player.player import Direction


class ShopNPC(NPC):
    """An NPC subclass that references a shop_id instead of dialogue."""

    def __init__(
        self,
        npc_id: str,
        name: str,
        x: int,
        y: int,
        sprite_name: str,
        facing: Direction,
        dialogue_id: str,
        shop_id: str,
    ) -> None:
        super().__init__(npc_id, name, x, y, sprite_name, facing, dialogue_id)
        self.shop_id = shop_id
