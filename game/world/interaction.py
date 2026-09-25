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
        from game.world.shop_npc import ShopNPC
        
        if isinstance(target, Trainer):
            logger.info(f"Interacted with Trainer {target.name}. Dialogue ID: {target.get_current_dialogue()}")
            if not target.has_battled:
                logger.info(f"Starting battle with Trainer {target.name}...")
                from game.states.dialogue_state import DialogueState
                from game.states.battle_state import BattleState
                from game.world.trainer_factory import TrainerFactory
                
                def start_battle():
                    tf = TrainerFactory.get_instance()
                    enemy_party = tf.create_party(target.trainer_id)
                    
                    if enemy_party:
                        battle_state = BattleState(self.game)
                        battle_params = {
                            "enemy_creature": enemy_party[0],
                            "is_trainer": True,
                            "trainer_id": target.trainer_id,
                            "trainer_party": enemy_party,
                            "trainer_npc": target
                        }
                        self.game.state_machine.push(battle_state, battle_params)
                    
                intro_text = target.trainer_data.get("dialogue_intro") or target.trainer_data.get("dialogue_start")
                dialogue_id = target.get_current_dialogue()
                if intro_text:
                    self.game.state_machine.push(DialogueState(self.game, dynamic_text=intro_text, speaker=target.name, on_complete=start_battle))
                elif dialogue_id:
                    self.game.state_machine.push(DialogueState(self.game, dialogue_id, on_complete=start_battle))
                else:
                    start_battle()
            else:
                defeat_text = target.trainer_data.get("dialogue_defeat")
                dialogue_id = target.get_current_dialogue()
                from game.states.dialogue_state import DialogueState
                if defeat_text:
                    self.game.state_machine.push(DialogueState(self.game, dynamic_text=defeat_text, speaker=target.name))
                elif dialogue_id:
                    self.game.state_machine.push(DialogueState(self.game, dialogue_id))
        elif isinstance(target, ShopNPC):
            logger.info(f"Interacted with ShopNPC {target.name}. Shop ID: {target.shop_id}")
            from game.states.shop_state import ShopState
            self.game.state_machine.push(ShopState(self.game), {"shop_id": target.shop_id})
        elif isinstance(target, NPC):
            dialogue_id = target.get_current_dialogue()
            logger.info(f"Interacted with NPC {target.name}. Dialogue ID: {dialogue_id}")
            from game.states.dialogue_state import DialogueState
            from game.quests.quest_manager import QuestManager
            
            qm = QuestManager.get_instance()
            msgs = qm.on_event("talk_npc", {"npc_id": target.npc_id})
            
            self.game.state_machine.push(DialogueState(self.game, dialogue_id))
            
            # If a quest was completed, we could show a toast, but DialogueState will cover the screen.
            # We'll just log it for now.
            for msg in msgs:
                logger.info(msg)
