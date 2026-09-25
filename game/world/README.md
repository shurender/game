# World Subsystem (`game/world/`)

The `world` package manages the overworld simulation, tile layers, 2D camera viewport tracking, collision detection, NPC interactions, map transitions, and story flags.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`world.py`** | High-level overworld manager (`World`). Manages active map instances, door/warp transitions, and steps grass encounter odds. |
| **`map.py`** | `Map` container. Holds multi-layer tile arrays (`ground`, `decoration`, `collision`), warp points, NPC lists, and encounter tables. |
| **`map_loader.py`** | Parser for `data/maps.json`. Deserializes maps, tilesets, NPC placements, and warp connections. |
| **`camera.py`** | Viewport camera (`Camera`). Centers the 480×320 logical camera on the player and clamps bounds cleanly, centering maps smaller than the screen. |
| **`collision.py`** | Collision resolver (`CollisionManager`). Validates tile walkability, impassable water/walls, NPC path blocking, and ledge hops. |
| **`npc.py`** | Base overworld character (`NPC`). Manages grid coordinates, sprite tags, facing directions, and dialogue lookups. |
| **`trainer.py`** | Battle-ready NPC (`Trainer`). Extends `NPC` with battle configurations, team IDs, and defeat tracking flags. |
| **`trainer_factory.py`** | Trainer builder (`TrainerFactory`). Reads `data/trainers.json` and creates enemy creature teams for battles. |
| **`shop_npc.py`** | Merchant NPC (`ShopNPC`). Dispatches player interactions directly into `ShopState`. |
| **`shop.py`** | Domain models for stores (`Shop`, `ShopListing`, `ShopTransaction`). Pure logic handling buying and selling items with `Wallet` and `Inventory`. |
| **`shop_factory.py`** | Reads `data/shops.json` to configure item listings, greetings, and sell price ratios. |
| **`interaction.py`** | Player interaction dispatcher (`InteractionManager`). Checks tile facing player, dispatches battles, dialogues, or shops. |
| **`progress_manager.py`** | Persistent story progress tracker (`WorldProgressManager`). Manages story flags (`defeated_trainer_x`, `has_creature`, etc.) and conditions. |

---

## Map Structure & Layers

Maps are defined with standard 32×32 pixel tiles:
1. **Ground Layer**: Base terrain (grass, paths, indoor floors, water).
2. **Decoration Layer**: Non-blocking cosmetic details (flowers, carpets, shadows).
3. **Collision Layer**: Grid of binary or passability flags (0 = walkable, 1 = solid barrier, 2 = one-way ledge).

---

## Interaction Flow

When the player presses `Action.CONFIRM` (`Z`, `Enter`, or `Space`):
1. `Player.interact()` calculates the target coordinate 1 tile in the facing direction.
2. `Map.get_npc_at(x, y)` checks for an NPC entity.
3. If an NPC is found, the NPC turns to face the player.
4. `InteractionManager.trigger_interaction(npc)` determines the target type:
   - **`Trainer`**: Displays intro dialogue, then pushes `BattleState`.
   - **`ShopNPC`**: Pushes `ShopState`.
   - **`NPC`**: Dispatches `talk_npc` event to `QuestManager` and pushes `DialogueState`.
