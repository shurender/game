# Game States Subsystem (`game/states/`)

The `states` package houses all UI and gameplay screens within the engine. Each state inherits from `State` (`base_state.py`) and is managed via the engine's `StateMachine`.

---

## State Inventory

| State Class | Module | Description |
| :--- | :--- | :--- |
| **`MainMenuState`** | `main_menu_state.py` | Title screen featuring particle effects, animated silhouette, save slot detection, and smooth fade transitions. |
| **`WorldState`** | `world_state.py` | Main overworld exploration state. Drives tilemap rendering, player movement, NPC interaction, camera tracking, and wild encounter triggers. |
| **`BattleState`** | `battle_state.py` | Turn-based battle screen. Controls fight/item/switch/run menus, creature entrance/faint animations, procedural capture animations, and turn resolution. |
| **`DialogueState`** | `dialogue_state.py` | Non-blocking modal overlay for NPC conversations. Supports typewriter text, branching choices, and game-state mutation actions (`start_quest`, `give_item`, `remove_item`, `give_creature`, `set_flag`). |
| **`PauseMenuState`** | `pause_state.py` | Sliding drawer menu accessed via `Tab`/`Esc`. Allows instant access to party, inventory, quest log, settings, and saving. |
| **`PartyState`** | `party_state.py` | Displays the player's 6-creature party, current HP bars, summary info, reordering/swapping, and in-battle switch selection. |
| **`InventoryState`** | `inventory_state.py` | Full-screen item bag with tabbed category filtering (`All`, `Healing`, `Capture`, `Stat Boost`, `Key Item`) and party/battle target selection. |
| **`ShopState`** | `shop_state.py` | Interactive shop interface with Buy/Sell tabs, item stock listings, and direct integration with `Wallet` and `ShopTransaction`. |
| **`EvolutionState`** | `evolution_state.py` | Full-screen evolution presentation featuring silhouette flashes, shape morphing, typewriter announcements, and stat delta summaries. |
| **`QuestLogState`** | `quest_log_state.py` | Tracks active and completed quests, displaying descriptions, objective checklists, and reward payouts. |
| **`SettingsState`** | `settings_state.py` | Audio and display configuration screen. Controls master, SFX, and BGM volume sliders, resolution presets, and fullscreen toggles. |

---

## State Lifecycle

Every `State` implements standard lifecycle hooks:
```python
class State:
    def enter(self, params: dict | None = None) -> None: ...
    def exit(self) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def handle_event(self, event: pygame.event.Event) -> None: ...
    def update(self, dt: float) -> None: ...
    def render(self, surface: pygame.Surface) -> None: ...
```

- When `DialogueState` or `PauseMenuState` is pushed onto the stack, the underlying `WorldState` receives `pause()`. Its update loop pauses while its rendered surface is retained underneath the overlay.
- When closed, `resume()` is triggered on the underlying state, seamlessly resuming music and input without reloading.
