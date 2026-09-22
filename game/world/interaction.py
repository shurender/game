"""Handles interactions between the player and NPCs/objects."""
from __future__ import annotations

import logging

logger = logging.getLogger("risu")

class InteractionManager:
    """Manages player interactions in the overworld."""
    
    def __init__(self, game):
        self.game = game

    def trigger_interaction(self, target) -> None:
        """Trigger an interaction with an NPC or object."""
        from game.world.npc import NPC
        from game.world.trainer import Trainer
        
        if isinstance(target, Trainer):
            logger.info(f"Interacted with Trainer {target.name}. Dialogue ID: {target.dialogue_id}")
            if not target.has_battled:
                logger.info(f"Starting battle with Trainer {target.name}...")
                from game.states.dialogue_state import DialogueState
                self.game.state_machine.push(DialogueState(self.game, target.dialogue_id))
        elif isinstance(target, NPC):
            logger.info(f"Interacted with NPC {target.name}. Dialogue ID: {target.dialogue_id}")
            from game.states.dialogue_state import DialogueState
            self.game.state_machine.push(DialogueState(self.game, target.dialogue_id))
