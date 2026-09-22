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
        self.player = Player(4, 6) # Default start position
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sprites = SpriteGenerator()
        self.interaction = InteractionManager(game)
        
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
            
            # Snap player pixel position
            self.player.pixel_x = float(self.player.x * TILE_SIZE)
            self.player.pixel_y = float(self.player.y * TILE_SIZE)
            self.player.is_moving = False
            
            self.camera.center_on(
                self.player.pixel_x + TILE_SIZE / 2,
                self.player.pixel_y + TILE_SIZE / 2
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            action = self.game.input.bindings.get(event.key)
            if action == Action.CANCEL:
                # Go back to main menu for now (placeholder for pause)
                self.game.state_machine.pop()
            elif action == Action.CONFIRM:
                # Try interaction
                ix, iy = self.player.interact()
                if self.world.current_map:
                    target_npc = self.world.current_map.get_npc_at(ix, iy)
                    if target_npc:
                        target_npc.face_player(self.player.x, self.player.y)
                        self.interaction.trigger_interaction(target_npc)

    def update(self, dt: float) -> None:
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
                # Trigger warp transition
                self.game.state_machine.replace(WorldState(self.game), {
                    "map_id": warp.target_map,
                    "x": warp.target_x,
                    "y": warp.target_y
                })
                return

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
