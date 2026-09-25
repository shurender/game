"""Battle State for the presentation layer of the battle engine."""
import pygame
import math
import random
from typing import Any

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.menu import Menu
from game.ui.dialogue_box import DialogueBox
from game.ui.text import render_text, render_text_outlined
from game.ui.components import draw_hp_bar
from game.battle.battle import Battle
from game.battle.battle_engine import BattleEngine
from game.battle.battle_action import BattleAction
from game.battle.ai import BattleAI
from game.battle.capture import BASIC_BALL, execute_capture
from game.creatures.creature_factory import CreatureFactory
from game.creatures.move import MoveFactory
from game.player.party import PartyManager
from game.states.party_state import PartyState
from game.states.inventory_state import InventoryState
from game.rendering.animation import AnimationLayer, HitFlash, CreatureEntranceAnim, CreatureFaintAnim, CaptureAnimation


class CreatureSprite:
    def __init__(self, creature, x, y, is_player, asset_manager=None):
        self.creature = creature
        self.x = x
        self.base_x = x
        self.base_y = y
        self.y = y
        self.is_player = is_player
        self.target_hp = creature.current_hp
        self.display_hp = float(creature.current_hp)
        self.shake_timer = 0.0
        
        # Load sprite via asset manager or use safe fallback
        self.image = None
        if asset_manager:
            species_id = getattr(getattr(creature, "species", None), "species_id", getattr(creature, "id", "florbit")).lower()
            sprite_name = f"creatures/{species_id}_{'back' if is_player else 'front'}"
            if asset_manager.has_image(sprite_name):
                self.image = asset_manager.get_image(sprite_name, size=(128, 128))
            elif asset_manager.has_image(f"creatures/{species_id}"):
                self.image = asset_manager.get_image(f"creatures/{species_id}", size=(128, 128))

        if self.image is None:
            color = COLORS["accent"] if is_player else COLORS["accent_warm"]
            if asset_manager:
                self.image = asset_manager.create_fallback_image(
                    width=128, height=128, label=creature.name[:3], color=color
                )
            else:
                self.image = pygame.Surface((128, 128))
                self.image.fill(color)
                pygame.draw.rect(self.image, COLORS["menu_border"], self.image.get_rect(), 4)
        
    def take_damage(self):
        self.target_hp = self.creature.current_hp
        self.shake_timer = 0.5
        
    def update(self, dt):
        # Smooth HP
        if self.display_hp > self.target_hp:
            self.display_hp -= (self.creature.stats.hp * 0.5) * dt
            if self.display_hp < self.target_hp:
                self.display_hp = self.target_hp
                
        # Shake effect
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.x = self.base_x + math.sin(self.shake_timer * 40) * 15
        else:
            self.x = self.base_x
            
    def render(self, surface, font):
        if self.creature.is_fainted and self.display_hp <= 0:
            return  # Don't draw fainted creature
            
        surface.blit(self.image, (self.x, self.y))
        
        # HUD Position
        hud_x = self.base_x + 150 if self.is_player else self.base_x - 180
        hud_y = self.base_y + 80 if self.is_player else self.base_y
        
        # Name and Level
        render_text_outlined(surface, f"{self.creature.name}  Lv.{self.creature.level}", font, hud_x, hud_y)
        
        # HP Bar
        bar_w = 160
        bar_h = 12
        draw_hp_bar(surface, hud_x, hud_y + 25, bar_w, bar_h, self.display_hp, self.creature.stats.hp)

            
        # HP numbers
        render_text_outlined(surface, f"{int(self.display_hp)}/{self.creature.stats.hp}", font, hud_x + bar_w - 60, hud_y + 45)


class BattleState(State):
    def __init__(self, game, wild_creature=None, enemy_creature=None) -> None:
        super().__init__(game)
        self._init_enemy_creature = enemy_creature or wild_creature
        self.font = self.game.assets.get_font(24)
        self.name_font = self.game.assets.get_font(20)
        
        self.dialogue_box = DialogueBox(self.font, self.name_font)
        
        self.phase = "INIT"
        self.battle = None
        self.player_sprite = None
        self.enemy_sprite = None
        
        self.main_menu = Menu(
            ["FIGHT", "SWITCH", "ITEM", "RUN"], 
            self.font, 
            SCREEN_WIDTH - 200, 
            SCREEN_HEIGHT - 120,
            spacing=30
        )
        self.main_menu.on_select = self._on_main_menu_select
        
        self.move_menu = None
        self.turn_result = None
        self.current_event_idx = 0
        
        # Animation layer — pure presentation, no game-logic side-effects
        self.anim = AnimationLayer(self.name_font)
        self.player_hit_flash = HitFlash()
        self.enemy_hit_flash = HitFlash()
        self._entrance_anim: CreatureEntranceAnim | None = None
        self._faint_anim: CreatureFaintAnim | None = None
        self._capture_anim: CaptureAnimation | None = None
        
    def enter(self, params: dict[str, Any] | None = None) -> None:
        params = params or {}
        
        party_mgr = PartyManager.get_instance()
        player_creature = party_mgr.get_first_available()
        enemy_creature = params.get("enemy_creature") or params.get("wild_creature") or getattr(self, "_init_enemy_creature", None)
        
        if not player_creature or not enemy_creature:
            # Fallback to test creatures if none provided
            cf = CreatureFactory.get_instance()
            if not player_creature:
                first_sp = next(iter(cf.species_db.keys()), "florbit")
                player_creature = cf.create_creature(first_sp, 5)
                party_mgr.add_creature(player_creature)
                
            if not enemy_creature:
                sp_keys = list(cf.species_db.keys())
                second_sp = sp_keys[1] if len(sp_keys) > 1 else (sp_keys[0] if sp_keys else "barkbug")
                enemy_creature = cf.create_creature(second_sp, 5)
            
        self.battle = Battle(player_creature, enemy_creature)
        
        self.player_sprite = CreatureSprite(self.battle.player_creature, 100, SCREEN_HEIGHT - 300, True, self.game.assets)
        self.enemy_sprite = CreatureSprite(self.battle.enemy_creature, SCREEN_WIDTH - 250, 100, False, self.game.assets)
        
        self.is_trainer = params.get("is_trainer", getattr(self, "is_trainer", False))
        self.trainer_id = params.get("trainer_id", getattr(self, "trainer_id", None))
        self.trainer_party = params.get("trainer_party", getattr(self, "trainer_party", []))
        self.trainer_npc = params.get("trainer_npc", getattr(self, "trainer_npc", None))
        self.enemy_party_idx = getattr(self, "enemy_party_idx", 0)
        
        ai_type = "BASIC"
        if self.is_trainer and self.trainer_npc and hasattr(self.trainer_npc, "trainer_data"):
            ai_type = self.trainer_npc.trainer_data.get("ai_type", "BASIC")
            
        self.enemy_ai = BattleAI(ai_type=ai_type)
        
        self.capture_data = None
        self._capture_anim: CaptureAnimation | None = None
        
        # Reset animation layer
        self.anim = AnimationLayer(self.name_font)
        self.player_hit_flash = HitFlash()
        self.enemy_hit_flash = HitFlash()
        
        # Entrance animation — enemy slides in from right
        enemy_target_x = SCREEN_WIDTH - 250
        self._entrance_anim = CreatureEntranceAnim(
            start_x=SCREEN_WIDTH + 50,
            end_x=enemy_target_x,
            y=100,
            duration=0.5,
        )
        self.enemy_sprite.x = SCREEN_WIDTH + 50
        self.enemy_sprite.base_x = enemy_target_x
        self._faint_anim = None
        
        # Fade-in transition
        self.anim.fade_out(duration=0.4)
        
        self.phase = "INTRO"
        if self.is_trainer:
            self.dialogue_box.start_text("", f"Trainer {self.trainer_npc.name} challenged you!\nTrainer {self.trainer_npc.name} sent out {self.battle.enemy_creature.name}!")
        else:
            self.dialogue_box.start_text("", f"A wild {self.battle.enemy_creature.name} appeared!")
        
        # Play battle music
        self.game.audio.music.play_battle_music(
            is_trainer=self.is_trainer,
            is_boss=getattr(self.trainer_npc, "trainer_data", {}).get("is_boss", False) if self.is_trainer and self.trainer_npc else False,
        )
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            is_confirm = False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_e):
                is_confirm = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_confirm = True

            if self.phase in ("INTRO", "ANIMATE_EVENTS", "BATTLE_END", "ANIMATE_CAPTURE_END", "ANIMATE_CAPTURE_FAIL"):
                if is_confirm:
                    if not self.dialogue_box.is_finished:
                        self.dialogue_box.skip_typing()
                    else:
                        self._advance_phase()
                        
            elif self.phase == "PLAYER_TURN":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_w):
                    self.main_menu.move_up()
                    self.game.audio.play_sound("menu_move")
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_DOWN, pygame.K_s):
                    self.main_menu.move_down()
                    self.game.audio.play_sound("menu_move")
                elif is_confirm:
                    self.game.audio.play_sound("menu_select")
                    self.main_menu.select()
                    
            elif self.phase == "MOVE_SELECT":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_w):
                    self.move_menu.move_up()
                    self.game.audio.play_sound("menu_move")
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_DOWN, pygame.K_s):
                    self.move_menu.move_down()
                    self.game.audio.play_sound("menu_move")
                elif is_confirm:
                    self.game.audio.play_sound("menu_select")
                    self.move_menu.select()
                elif (event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_x)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
                    self.game.audio.play_sound("menu_cancel")
                    self.phase = "PLAYER_TURN"

    def _on_main_menu_select(self, idx: int, text: str):
        if text == "FIGHT":
            self._setup_move_menu()
            self.phase = "MOVE_SELECT"
        elif text == "RUN":
            if self.is_trainer:
                self.phase = "ANIMATE_EVENTS"
                self.dialogue_box.start_text("", "You can't run from a trainer battle!")
                # Give the enemy a free action because the player tried to run? No, just block it.
                # Actually, let's just make it a free message, then return to player turn.
                # But ANIMATE_EVENTS advances to BATTLE_END or PLAYER_TURN.
                # Let's just create a dummy turn result so it shows the message and goes back to PLAYER_TURN.
                from game.battle.battle_result import TurnResult, ActionEvent
                self.turn_result = TurnResult()
                self.turn_result.events.append(ActionEvent(
                    actor_name=self.battle.player_creature.name,
                    action_type="MESSAGE",
                    message="You can't run from a trainer battle!"
                ))
                self.current_event_idx = 0
            else:
                self._execute_turn(BattleAction(self.battle.player_creature, "ESCAPE"))
        elif text == "SWITCH":
            self.game.state_machine.push(PartyState(self.game), {"mode": "BATTLE_SWITCH", "on_select": self._on_party_switch})
        elif text == "ITEM":
            self.game.state_machine.push(
                InventoryState(self.game),
                {
                    "mode": "BATTLE_USE",
                    "battle": self.battle,
                    "on_use": self._on_item_used_in_battle,
                }
            )

    def _setup_move_menu(self):
        mf = MoveFactory.get_instance()
        move_names = []
        self._current_moves = []
        for m_id in self.battle.player_creature.moves:
            m = mf.get_move(m_id)
            move_names.append(m.name)
            self._current_moves.append(m)
            
        self.move_menu = Menu(
            move_names,
            self.font,
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 150,
            spacing=30
        )
        self.move_menu.on_select = self._on_move_select
        
    def _on_party_switch(self, creature):
        if creature == self.battle.player_creature:
            # Already active
            return
            
        action = BattleAction(
            actor=self.battle.player_creature,
            action_type="SWITCH",
            target=creature
        )
        self._execute_turn(action)
        # Update sprite immediately so it's correct during events if needed
        # Or wait for the event? The event processor will just state it happened.
        # Let's just update the sprite.
        self.player_sprite = CreatureSprite(creature, 100, SCREEN_HEIGHT - 300, True, self.game.assets)

    def _on_item_used_in_battle(self, item_id: str, creature) -> None:
        """Called by InventoryState after an item use during battle."""
        from game.inventory.inventory import Inventory
        from game.inventory.item_factory import ItemFactory
        from game.battle.capture import execute_capture
        from game.rendering.animation import CaptureAnimation
        
        inv = Inventory.get_instance()
        item = ItemFactory.get_instance().get(item_id)
        if not item:
            return
        
        if item.category == "Capture":
            if self.is_trainer:
                self.phase = "ANIMATE_EVENTS"
                self.dialogue_box.start_text("", "You can't catch another trainer's creature!")
                from game.battle.battle_result import TurnResult, ActionEvent
                self.turn_result = TurnResult()
                self.turn_result.events.append(ActionEvent(
                    actor_name=self.battle.player_creature.name,
                    action_type="MESSAGE",
                    message="You can't catch another trainer's creature!"
                ))
                self.current_event_idx = 0
                return
                
            # Consume item and calculate success
            inv.remove(item_id, 1)
            target_creature = creature or self.battle.enemy_creature
            success, shakes, location = execute_capture(
                target_creature, item
            )
            self.capture_data = {
                "success": success,
                "shakes": shakes,
                "location": location
            }
            
            # Start capture animation
            self.phase = "ANIMATE_CAPTURE"
            start_pos = (int(self.player_sprite.x + 30), int(self.player_sprite.y + 30))
            target_pos = (int(self.enemy_sprite.x + 30), int(self.enemy_sprite.y + 30))
            
            def _on_finish():
                if success:
                    loc_text = "Party" if location == "PARTY" else "Storage Box"
                    self.dialogue_box.start_text("", f"Gotcha! {target_creature.name} was caught!\nSent to {loc_text}.")
                    self.phase = "ANIMATE_CAPTURE_END"
                else:
                    self.dialogue_box.start_text("", "Oh no! The creature broke free!")
                    self.phase = "ANIMATE_CAPTURE_FAIL"
                    
            self._capture_anim = CaptureAnimation(
                start=start_pos,
                target=target_pos,
                shakes=shakes,
                success=success,
                on_finish=_on_finish
            )
            return
            
        # Give the enemy a free action because the player spent their turn healing/etc.
        enemy_action = self.enemy_ai.choose_action(
            self.battle, self.battle.enemy_creature, self.battle.player_creature
        )
        # Player effectively passes this turn (ITEM action)
        player_action = BattleAction(self.battle.player_creature, "ITEM")
        self.turn_result = BattleEngine.process_turn(self.battle, player_action, enemy_action)
        self.current_event_idx = 0
        self._process_next_event()

    def _on_move_select(self, idx: int, text: str):
        selected_move = self._current_moves[idx]
        action = BattleAction(
            actor=self.battle.player_creature,
            action_type="MOVE",
            target=self.battle.enemy_creature,
            move=selected_move
        )
        self._execute_turn(action)
        
    def _execute_turn(self, player_action: BattleAction):
        # AI selects a move based on its strategy
        enemy_action = self.enemy_ai.choose_action(self.battle, self.battle.enemy_creature, self.battle.player_creature)
        
        self.turn_result = BattleEngine.process_turn(self.battle, player_action, enemy_action)
        self.current_event_idx = 0
        self._process_next_event()
        
    def _process_next_event(self):
        if self.turn_result and self.current_event_idx < len(self.turn_result.events):
            event = self.turn_result.events[self.current_event_idx]
            self.current_event_idx += 1
            
            self.phase = "ANIMATE_EVENTS"
            self.dialogue_box.start_text("", event.message)
            
            # Trigger shake / HP decrease
            if event.damage_dealt > 0:
                if event.actor_name == self.battle.player_creature.name:
                    self.enemy_sprite.take_damage()
                    self.enemy_hit_flash.trigger()
                    self.anim.shake.trigger(duration=0.25, magnitude=6)
                    # Floating damage number over enemy
                    self.anim.spawn_damage_number(
                        self.enemy_sprite.base_x + 64,
                        self.enemy_sprite.y + 20,
                        event.damage_dealt,
                        color=(255, 80, 80),
                    )
                    self.game.audio.play_attack_sound()
                else:
                    self.player_sprite.take_damage()
                    self.player_hit_flash.trigger()
                    self.anim.spawn_damage_number(
                        self.player_sprite.base_x + 64,
                        self.player_sprite.y + 20,
                        event.damage_dealt,
                        color=(255, 140, 60),
                    )
                    self.game.audio.play_attack_sound()
                    
            if event.action_type == "SWITCH":
                # Ensure sprite matches the engine state
                if event.actor_name == self.battle.player_creature.name or self.battle.player_creature.name in event.message:
                    # Update sprite reference if not already done
                    self.player_sprite = CreatureSprite(self.battle.player_creature, 100, SCREEN_HEIGHT - 300, True, self.game.assets)
                    
        else:
            if self.battle.is_over or self.battle.player_creature.is_fainted:
                # Handle fainted player creature
                if self.battle.player_creature.is_fainted:
                    party_mgr = PartyManager.get_instance()
                    if party_mgr.has_usable_creatures():
                        party_state = PartyState(self.game)
                        self.game.state_machine.push(party_state, {"mode": "BATTLE_SWITCH", "on_select": self._on_forced_switch})
                        return
                    else:
                        self.battle.is_over = True
                        self.battle.winner = "ENEMY"
                        
                # Check if trainer has more creatures
                if self.battle.winner == "PLAYER" and self.is_trainer:
                    next_creature = None
                    for i in range(self.enemy_party_idx + 1, len(self.trainer_party)):
                        if not self.trainer_party[i].is_fainted:
                            next_creature = self.trainer_party[i]
                            self.enemy_party_idx = i
                            break
                    
                    if next_creature:
                        self.battle.is_over = False
                        self.battle.winner = None
                        self.battle.enemy_creature = next_creature
                        self.enemy_sprite = CreatureSprite(next_creature, SCREEN_WIDTH - 250, 100, False, self.game.assets)
                        self.phase = "ANIMATE_EVENTS"
                        self.dialogue_box.start_text("", f"Trainer {self.trainer_npc.name} sent out {next_creature.name}!")
                        return

                self.phase = "BATTLE_END"
                if self.battle.winner == "PLAYER":
                    if self.is_trainer and self.trainer_npc:
                        self.trainer_npc.has_battled = True
                        from game.world.progress_manager import WorldProgressManager
                        WorldProgressManager.get_instance().set_flag(f"defeated_{self.trainer_id}", True)
                        self.dialogue_box.start_text("", f"You defeated Trainer {self.trainer_npc.name}!")
                    else:
                        self.dialogue_box.start_text("", "You won the battle!")
                elif self.battle.winner == "ENEMY":
                    self.dialogue_box.start_text("", "You blacked out!")
                else:
                    self.dialogue_box.start_text("", "Got away safely!")
            else:
                self.phase = "PLAYER_TURN"
                self.dialogue_box.start_text("", f"What will {self.battle.player_creature.name} do?")
                self.dialogue_box.skip_typing()

    def _advance_phase(self):
        if self.phase == "INTRO":
            self.phase = "PLAYER_TURN"
            self.dialogue_box.start_text("", f"What will {self.battle.player_creature.name} do?")
            self.dialogue_box.skip_typing()
        elif self.phase == "ANIMATE_CAPTURE_END":
            self.phase = "BATTLE_END"
        elif self.phase == "ANIMATE_CAPTURE_FAIL":
            self.phase = "ANIMATE_EVENTS"
            self._capture_anim = None
            # Enemy attacks after player fails capture
            enemy_action = self.enemy_ai.choose_action(self.battle, self.battle.enemy_creature, self.battle.player_creature)
            self.turn_result = BattleEngine.process_turn(self.battle, BattleAction(self.battle.player_creature, "ITEM"), enemy_action)
            self.current_event_idx = 0
            self._process_next_event()
        elif self.phase == "ANIMATE_EVENTS":
            if self.turn_result and self.current_event_idx < len(self.turn_result.events):
                self._process_next_event()
            else:
                if self.battle.is_over or self.battle.player_creature.is_fainted:
                    if self.battle.player_creature.is_fainted:
                        party_mgr = PartyManager.get_instance()
                        if party_mgr.has_usable_creatures():
                            party_state = PartyState(self.game)
                            self.game.state_machine.push(party_state, {"mode": "BATTLE_SWITCH", "on_select": self._on_forced_switch})
                            return
                        else:
                            self.battle.is_over = True
                            self.battle.winner = "ENEMY"
                            
                    # Check if trainer has more creatures
                    if self.battle.winner == "PLAYER" and self.is_trainer:
                        # Find next healthy creature
                        next_creature = None
                        for i in range(self.enemy_party_idx + 1, len(self.trainer_party)):
                            if not self.trainer_party[i].is_fainted:
                                next_creature = self.trainer_party[i]
                                self.enemy_party_idx = i
                                break
                        
                        if next_creature:
                            self.battle.is_over = False
                            self.battle.winner = None
                            self.battle.enemy_creature = next_creature
                            self.enemy_sprite = CreatureSprite(next_creature, SCREEN_WIDTH - 250, 100, False, self.game.assets)
                            
                            self.phase = "ANIMATE_EVENTS"
                            # We hack a custom event for the dialogue
                            self.dialogue_box.start_text("", f"Trainer {self.trainer_npc.name} sent out {next_creature.name}!")
                            return

                    self.phase = "BATTLE_END"
                    if self.battle.winner == "PLAYER":
                        if self.is_trainer and self.trainer_npc:
                            self.trainer_npc.has_battled = True
                            from game.world.progress_manager import WorldProgressManager
                            WorldProgressManager.get_instance().set_flag(f"defeated_{self.trainer_id}", True)
                            self.dialogue_box.start_text("", f"You defeated Trainer {self.trainer_npc.name}!")
                        else:
                            self.dialogue_box.start_text("", "You won the battle!")
                    elif self.battle.winner == "ENEMY":
                        self.dialogue_box.start_text("", "You blacked out!")
                    else:
                        self.dialogue_box.start_text("", "Got away safely!")
                else:
                    self.phase = "PLAYER_TURN"
                    self.dialogue_box.start_text("", f"What will {self.battle.player_creature.name} do?")
                    self.dialogue_box.skip_typing()
        elif self.phase == "BATTLE_END":
            # Fire Quest Events & Trainer rewards BEFORE popping state
            from game.quests.quest_manager import QuestManager
            import logging
            logger = logging.getLogger("risu")
            qm = QuestManager.get_instance()
            
            if self.battle.winner == "PLAYER":
                msgs = qm.on_event("defeat_creature", {"species_id": self.battle.enemy_creature.species.species_id})
                for msg in msgs:
                    logger.info(msg)
                    
                if self.is_trainer and self.trainer_npc:
                    self.trainer_npc.has_battled = True
                    msgs = qm.on_event("defeat_trainer", {"trainer_id": self.trainer_id})
                    for msg in msgs:
                        logger.info(msg)
                        
                    from game.world.progress_manager import WorldProgressManager
                    pm = WorldProgressManager.get_instance()
                    pm.set_flag(f"defeated_{self.trainer_id}", True)
                        
                    # Grant trainer rewards
                    from game.inventory.inventory import Inventory
                    from game.player.wallet import Wallet
                    
                    if hasattr(self.trainer_npc, "trainer_data"):
                        rewards = self.trainer_npc.trainer_data.get("rewards", {})
                        coins = self.trainer_npc.trainer_data.get("reward_money", rewards.get("coins", 0))
                        if coins > 0:
                            Wallet.get_instance().coins += coins
                            logger.info(f"Received {coins} coins from {self.trainer_npc.name}!")
                        for item in rewards.get("items", []):
                            Inventory.get_instance().add(item["item_id"], item.get("quantity", 1))
                            logger.info(f"Received {item.get('quantity', 1)}x {item['item_id']} from {self.trainer_npc.name}!")
                            
            elif self.capture_data and self.capture_data.get("success"):
                msgs = qm.on_event("capture_creature", {"species_id": self.battle.enemy_creature.species.species_id})
                for msg in msgs:
                    logger.info(msg)

            if self.battle.winner == "ENEMY":
                party_mgr = PartyManager.get_instance()
                for c in party_mgr.party:
                    c.current_hp = c.stats.hp
                    c.status = None
                from game.states.world_state import WorldState
                self.game.state_machine.clear()
                self.game.state_machine.push(WorldState(self.game), {
                    "map_id": "player_house",
                    "x": 4,
                    "y": 6
                })
                return

            self.game.state_machine.pop()

            if self.turn_result and self.turn_result.xp_result and self.turn_result.xp_result.pending_evolution:
                from game.states.evolution_state import EvolutionState
                from game.creatures.creature_factory import CreatureFactory
                
                creature = self.battle.player_creature
                target_id = self.turn_result.xp_result.evolution_target
                cf = CreatureFactory.get_instance()
                
                try:
                    evo_res = cf.evolve_creature(creature, target_id)
                    evo_state = EvolutionState(self.game)
                    self.game.state_machine.push(evo_state, {
                        "creature": creature,
                        "evo_result": evo_res
                    })
                except Exception as e:
                    logger.error(f"Evolution error: {e}")
    def _on_forced_switch(self, creature):
        self.battle.player_creature = creature
        self.player_sprite = CreatureSprite(creature, 100, SCREEN_HEIGHT - 300, True, self.game.assets)
        self.phase = "PLAYER_TURN"
        self.dialogue_box.start_text("", f"Go, {creature.name}!")
            
    def update(self, dt: float) -> None:
        self.dialogue_box.update(dt)
        self.player_sprite.update(dt)
        self.enemy_sprite.update(dt)
        self.anim.update(dt)
        self.player_hit_flash.update(dt)
        self.enemy_hit_flash.update(dt)
        
        # Entrance animation drives enemy x position
        if self._entrance_anim and not self._entrance_anim.is_done:
            self._entrance_anim.update(dt)
            self.enemy_sprite.x = self._entrance_anim.current_x
            self.enemy_sprite.base_x = self._entrance_anim.end_x
        
        # Faint animation
        if self._faint_anim and not self._faint_anim.is_done:
            self._faint_anim.update(dt)
        
        # Capture animation
        if self._capture_anim and not self._capture_anim.is_done:
            self._capture_anim.update(dt)
        
        if self.phase == "PLAYER_TURN":
            self.main_menu.update(dt)
        elif self.phase == "MOVE_SELECT" and self.move_menu:
            self.move_menu.update(dt)
            
    def render(self, surface: pygame.Surface) -> None:
        # Apply screen shake offset
        shake_off = self.anim.shake.get_offset()
        
        # Background
        surface.fill(COLORS["bg_medium"])
        
        # Draw arena bases
        pygame.draw.ellipse(surface, (40, 40, 60), (50 + shake_off[0], SCREEN_HEIGHT - 200 + shake_off[1], 300, 100))
        pygame.draw.ellipse(surface, (40, 40, 60), (SCREEN_WIDTH - 350 + shake_off[0], 200 + shake_off[1], 300, 100))
        
        # Capture animation handles enemy visibility
        show_enemy = not (self._capture_anim and not self._capture_anim.is_done and self._capture_anim._phase >= 1)
        
        # Faint anim: draw enemy at offset position with fading alpha
        if self._faint_anim and not self._faint_anim.is_done:
            # draw with faint anim alpha
            enemy_surf = self.enemy_sprite.image.copy()
            enemy_surf.set_alpha(self._faint_anim.alpha)
            ex = int(self.enemy_sprite.x + shake_off[0])
            ey = int(self._faint_anim.current_y + shake_off[1])
            surface.blit(enemy_surf, (ex, ey))
        elif show_enemy:
            # Apply hit flash
            if self.enemy_hit_flash.visible:
                sprite_to_draw = self.enemy_hit_flash.apply(self.enemy_sprite.image)
                surface.blit(sprite_to_draw, (int(self.enemy_sprite.x + shake_off[0]), int(self.enemy_sprite.y + shake_off[1])))
            else:
                self.enemy_sprite.render(surface, self.name_font)
            
        # Player sprite with hit flash
        if self.player_hit_flash.visible:
            sprite_to_draw = self.player_hit_flash.apply(self.player_sprite.image)
            surface.blit(sprite_to_draw, (int(self.player_sprite.x + shake_off[0]), int(self.player_sprite.y + shake_off[1])))
        else:
            self.player_sprite.render(surface, self.name_font)
        
        # Capture animation
        if self._capture_anim and not self._capture_anim.is_done:
            self._capture_anim.render(surface)
            # Scale creature to match capture shrink phase
            if self._capture_anim.creature_scale > 0 and self._capture_anim._phase == 1:
                s = max(0.05, self._capture_anim.creature_scale)
                orig = self.enemy_sprite.image
                w = max(1, int(orig.get_width() * s))
                h = max(1, int(orig.get_height() * s))
                scaled = pygame.transform.scale(orig, (w, h))
                cx = int(self.enemy_sprite.base_x + 64 - w // 2)
                cy = int(self.enemy_sprite.y + 64 - h // 2)
                surface.blit(scaled, (cx, cy))
        
        # Animation layer overlays (damage numbers, level-up, fade)
        self.anim.render(surface)
        
        # Dialogue Box
        if self.phase != "PLAYER_TURN" and self.phase != "MOVE_SELECT":
            self.dialogue_box.render(surface)
        elif self.phase == "PLAYER_TURN":
            self.dialogue_box.render(surface)
            # Render menu background
            menu_rect = pygame.Rect(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 140, 200, 140)
            pygame.draw.rect(surface, COLORS["menu_bg"], menu_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], menu_rect, width=4, border_radius=8)
            self.main_menu.draw(surface)
        elif self.phase == "MOVE_SELECT" and self.move_menu:
            self.dialogue_box.render(surface)
            menu_rect = pygame.Rect(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 170, 220, 170)
            pygame.draw.rect(surface, COLORS["menu_bg"], menu_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], menu_rect, width=4, border_radius=8)
            self.move_menu.draw(surface)
