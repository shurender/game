"""State for displaying and interacting with dialogue."""
import pygame
import logging
from typing import Callable

from game.states.base_state import State
from game.core.input_handler import Action
from game.ui.dialogue_manager import DialogueManager
from game.ui.dialogue_box import DialogueBox

logger = logging.getLogger("risu")

class DialogueState(State):
    """Handles the display and progression of dialogue."""
    
    def __init__(self, game, dialogue_id: str = "", on_complete: Callable | None = None, dynamic_text: str = None):
        super().__init__(game)
        self.dialogue_id = dialogue_id
        self.on_complete_callback = on_complete
        
        self.dialogue_manager = DialogueManager()
        
        # Load fonts
        font = self.game.assets.get_font(24)
        name_font = self.game.assets.get_font(28)
        
        self.box = DialogueBox(font, name_font)
        
        if dynamic_text:
            self.current_node_data = {}
            self.box.start_text(speaker="", text=dynamic_text)
        else:
            # Start at the root node
            self.current_node_data = {}
            self.current_node_id = "start"
            self._load_node(self.current_node_id)
        
    def _load_node(self, node_id: str) -> None:
        node = self.dialogue_manager.get_node(self.dialogue_id, node_id)
        if not node:
            logger.error(f"Dialogue node not found: {self.dialogue_id}.{node_id}")
            self._close()
            return
            
        # Execute actions if present
        if "actions" in node:
            for action in node["actions"]:
                self._execute_action(action)
            
        self.box.start_text(
            speaker=node.get("speaker", ""),
            text=node.get("text", ""),
            choices=node.get("choices")
        )
        self.current_node_data = node
        
    def _execute_action(self, action: dict) -> None:
        action_type = action.get("type")
        if action_type == "set_flag":
            from game.world.progress_manager import WorldProgressManager
            pm = WorldProgressManager.get_instance()
            pm.set_flag(action.get("flag", ""), action.get("value", True))
            logger.info(f"Dialogue Action: Set flag {action.get('flag')} to {action.get('value', True)}")
        elif action_type == "give_item":
            from game.inventory.inventory import Inventory
            inv = Inventory.get_instance()
            inv.add(action.get("item", ""), action.get("qty", 1))
            logger.info(f"Dialogue Action: Received item {action.get('item')} x{action.get('qty', 1)}")
        elif action_type == "give_creature":
            from game.player.party import Party
            from game.creatures.creature import Creature
            party = Party.get_instance()
            if not party.is_full():
                creature_id = action.get("creature", "")
                level = action.get("level", 5)
                c = Creature(creature_id, level)
                party.add_creature(c)
                logger.info(f"Dialogue Action: Received creature {creature_id} Lv{level}")
        
    def _close(self) -> None:
        self.game.state_machine.pop()
        if self.on_complete_callback:
            self.on_complete_callback()
            
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            action = self.game.input.bindings.get(event.key)
            
            if action == Action.CONFIRM:
                if not self.box.is_finished:
                    # Skip typewriter
                    self.box.skip_typing()
                    self.game.audio.play_sfx("menu_select")
                else:
                    # Advance
                    self.game.audio.play_sfx("menu_select")
                    if self.box.choices:
                        # Follow choice
                        choice = self.box.choices[self.box.selected_choice]
                        if "next" in choice:
                            self._load_node(choice["next"])
                        else:
                            self._close()
                    else:
                        # Follow next node or close
                        next_node = self.current_node_data.get("next")
                        if next_node:
                            self._load_node(next_node)
                        else:
                            self._close()
            
            elif action == Action.UP and self.box.is_finished and self.box.choices:
                self.box.move_choice(-1)
                self.game.audio.play_sfx("menu_select")
            elif action == Action.DOWN and self.box.is_finished and self.box.choices:
                self.box.move_choice(1)
                self.game.audio.play_sfx("menu_select")

    def update(self, dt: float) -> None:
        self.box.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # We don't clear the screen because we want to draw OVER the previous state (the world).
        # But we actually don't have control over drawing the world from here unless we tell the state machine to draw lower states.
        # StateMachine's render method only renders the *current* state.
        # I should probably update StateMachine.render to render the whole stack or let this state request a snapshot.
        # For now, it will draw on top of whatever was there (which remains on the buffer because we don't clear in this state).
        self.box.render(surface)

