"""World state — handles overworld exploration, movement, and map rendering."""
from __future__ import annotations

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from game.states.base_state import State
from game.core.input_handler import Action
from game.world.world import World
from game.player.player import Player, Direction
from game.world.camera import Camera
from game.world.collision import CollisionManager
from game.world.interaction import InteractionManager
from game.rendering.sprite_generator import SpriteGenerator
from game.world.tile import get_tile_info


class WorldState(State):
    """The main overworld exploration state."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.world = World(game)
        self.player = Player(4, 6)  # Default start position
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sprites = SpriteGenerator()
        self.interaction = InteractionManager(game)
        self._paused: bool = False  # True while a sub-state is above us
        
        # Pre-load starting map
        self.world.load_map("starting_town")
        self.collision = CollisionManager(self.world.current_map)
        
        # Initialize camera position immediately
        self.camera.center_on(
            self.player.x * TILE_SIZE + TILE_SIZE / 2,
            self.player.y * TILE_SIZE + TILE_SIZE / 2
        )

    def enter(self, params=None) -> None:
        if params and "map_id" in params:
            self.world.load_map(params["map_id"])
            self.collision = CollisionManager(self.world.current_map)
            if "x" in params: self.player.x = params["x"]
            if "y" in params: self.player.y = params["y"]
            if "facing" in params:
                try:
                    from game.player.player import Direction
                    if isinstance(params["facing"], str):
                        self.player.facing = Direction[params["facing"]]
                    else:
                        self.player.facing = params["facing"]
                except KeyError:
                    pass
            
            # Snap player pixel position
            self.player.pixel_x = float(self.player.x * TILE_SIZE)
            self.player.pixel_y = float(self.player.y * TILE_SIZE)
            self.player.is_moving = False
            
            self.camera.center_on(
                self.player.pixel_x + TILE_SIZE / 2,
                self.player.pixel_y + TILE_SIZE / 2
            )

    # ------------------------------------------------------------------ #
    #  Pause / resume (called by StateMachine when sub-states are pushed)  #
    # ------------------------------------------------------------------ #

    def pause(self) -> None:
        """Freeze world updates while a sub-state (pause menu, battle, etc.) is active."""
        self._paused = True

    def resume(self) -> None:
        """Resume world updates when the sub-state above us is popped."""
        self._paused = False
        # Play world music again in case battle music was playing
        if self.world.current_map:
            self.game.audio.music.play_world_music(self.world.current_map.map_id)

    # ------------------------------------------------------------------ #
    #  Input                                                               #
    # ------------------------------------------------------------------ #

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            action = self.game.input.bindings.get(event.key)
            if action in (Action.CANCEL, Action.MENU, Action.START):
                # Open the pause menu
                from game.states.pause_state import PauseMenuState
                self.game.state_machine.push(PauseMenuState(self.game))
            elif action == Action.CONFIRM:
                # Try interaction
                ix, iy = self.player.interact()
                if self.world.current_map:
                    target_npc = self.world.current_map.get_npc_at(ix, iy)
                    if target_npc:
                        target_npc.face_player(self.player.x, self.player.y)
                        self.interaction.trigger_interaction(target_npc)
            elif action == Action.SAVE:
                from game.core.save_manager import SaveManager
                success = SaveManager(self.game).save(slot=1)
                from game.states.dialogue_state import DialogueState
                msg = "Game saved!" if success else "Save failed."
                self.game.state_machine.push(DialogueState(self.game, dynamic_text=msg))
                self.game.audio.play_sound("menu_select")


    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> None:
        # The StateMachine only calls update on the TOP state, so this guard
        # is a safety net for any code that calls update() directly.
        if self._paused:
            return

        # Handle continuous movement input
        if not self.player.is_moving and not self.world.transitioning:
            dx, dy = 0, 0
            facing = None
            
            if self.game.input.is_pressed(Action.UP):
                dy = -1
                facing = Direction.UP
            elif self.game.input.is_pressed(Action.DOWN):
                dy = 1
                facing = Direction.DOWN
            elif self.game.input.is_pressed(Action.LEFT):
                dx = -1
                facing = Direction.LEFT
            elif self.game.input.is_pressed(Action.RIGHT):
                dx = 1
                facing = Direction.RIGHT
                
            if dx != 0 or dy != 0:
                # Only move horizontally or vertically, not diagonally
                if dx != 0 and dy != 0:
                    dy = 0 # Prioritize horizontal
                
                target_x = self.player.x + dx
                target_y = self.player.y + dy
                
                if self.world.current_map and self.collision.is_walkable(target_x, target_y):
                    self.player.start_move(dx, dy)
                elif facing:
                    # Turn to face obstacle
                    self.player.turn(facing)
                    
        self.player.update(dt)
        
        # Check warps after movement completes
        if not self.player.is_moving and self.world.current_map:
            warp = self.world.current_map.get_warp_at(self.player.x, self.player.y)
            if warp:
                # Autosave before warping
                from game.core.save_manager import SaveManager
                SaveManager(self.game).save(slot=0) # Slot 0 is autosave
                
                # Trigger warp transition
                self.game.state_machine.replace(WorldState(self.game), {
                    "map_id": warp.target_map,
                    "x": warp.target_x,
                    "y": warp.target_y
                })
                return
                
            # Check wild encounters
            if self.world.current_map.is_encounter(self.player.x, self.player.y):
                import random
                if random.random() < 0.15: # 15% chance per step
                    wild = self.world.current_map.generate_wild_encounter()
                    if wild:
                        from game.states.battle_state import BattleState
                        from game.player.party import Party
                        party = Party.get_instance()
                        # Only start battle if party is not empty and has conscious creatures
                        if not party.is_empty() and any(c.current_hp > 0 for c in party.creatures):
                            # Play transition sound or stop music here if needed
                            self.game.state_machine.push(BattleState(self.game, wild_creature=wild))
                            return
                
            # Check trainer line of sight
            from game.world.trainer import Trainer
            for npc in self.world.current_map.npcs:
                if isinstance(npc, Trainer) and not npc.has_battled:
                    if self._check_trainer_sight(npc):
                        npc.face_player(self.player.x, self.player.y)
                        # We could walk the trainer to the player here, but for now just trigger interaction
                        self.interaction.trigger_interaction(npc)
                        break

        # Update camera to follow player smoothly
        self.camera.follow(
            self.player.pixel_x + TILE_SIZE / 2,
            self.player.pixel_y + TILE_SIZE / 2,
            dt
        )
        if self.world.current_map:
            self.camera.clamp_to_map(
                self.world.current_map.width * TILE_SIZE,
                self.world.current_map.height * TILE_SIZE
            )


    def _check_trainer_sight(self, trainer) -> bool:
        from game.player.player import Direction
        if trainer.sight_range <= 0:
            return False
            
        dx, dy = 0, 0
        if trainer.facing == Direction.UP: dy = -1
        elif trainer.facing == Direction.DOWN: dy = 1
        elif trainer.facing == Direction.LEFT: dx = -1
        elif trainer.facing == Direction.RIGHT: dx = 1
        
        for i in range(1, trainer.sight_range + 1):
            check_x = trainer.x + dx * i
            check_y = trainer.y + dy * i
            
            if self.player.x == check_x and self.player.y == check_y:
                return True
                
            # Stop vision on collision
            if not self.collision.is_walkable(check_x, check_y):
                break
                
        return False

    def render(self, surface: pygame.Surface) -> None:
        self.game.renderer.clear((0, 0, 0))
        

        if not self.world.current_map:
            return

        map_data = self.world.current_map
        
        # Determine visible tile range
        start_col = max(0, int(self.camera.x) // TILE_SIZE)
        end_col = min(map_data.width, int(self.camera.x + SCREEN_WIDTH) // TILE_SIZE + 2)
        start_row = max(0, int(self.camera.y) // TILE_SIZE)
        end_row = min(map_data.height, int(self.camera.y + SCREEN_HEIGHT) // TILE_SIZE + 2)
        
        # Draw ground layer
        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                if map_data.ground:
                    tile_id = map_data.ground[y][x]
                    tile_info = get_tile_info(tile_id)
                    tile_surf = self.sprites.get_tile_surface(tile_info, x, y)
                    
                    screen_x, screen_y = self.camera.apply(x * TILE_SIZE, y * TILE_SIZE)
                    surface.blit(tile_surf, (screen_x, screen_y))
        
        # Draw NPCs
        for npc in map_data.npcs:
            npc_surf = self.sprites.get_player_sprite(npc.facing, False, 0.0) # Using player sprite generator as placeholder
            screen_x, screen_y = self.camera.apply(npc.x * TILE_SIZE, npc.y * TILE_SIZE)
            surface.blit(npc_surf, (screen_x, screen_y))
        
        # Draw player
        player_surf = self.sprites.get_player_sprite(
            self.player.facing, 
            self.player.is_moving, 
            self.player.anim_timer
        )
        px, py = self.camera.apply(self.player.pixel_x, self.player.pixel_y)
        surface.blit(player_surf, (px, py))
