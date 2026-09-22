"""Main Game class — owns the loop, state machine, and all subsystems."""
from __future__ import annotations

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, SHOW_FPS, COLORS, logger
from game.core.state_machine import StateMachine
from game.core.input_handler import InputHandler
from game.core.asset_manager import AssetManager
from game.rendering.renderer import Renderer
from game.audio.audio_manager import AudioManager


class Game:
    """Top-level game object.

    Creates the Pygame display, initialises all subsystems, and drives
    the main loop: events → update → draw.
    """

    def __init__(self) -> None:
        logger.info("Initializing game engine...")
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.running: bool = True

        # Subsystems
        self.state_machine = StateMachine()
        self.input = InputHandler()
        self.assets = AssetManager()
        self.renderer = Renderer(self.screen)
        self.audio = AudioManager()

        # Pre-synthesize common UI sounds
        self.audio.synthesize_tone(
            "menu_move", frequency=600, duration=0.06,
            wave="square", volume=0.2,
        )
        self.audio.synthesize_tone(
            "menu_select", frequency=800, duration=0.1,
            wave="square", volume=0.25,
        )
        self.audio.synthesize_tone(
            "menu_cancel", frequency=300, duration=0.1,
            wave="square", volume=0.2,
        )

        # Push the initial state
        from game.states.main_menu_state import MainMenuState
        self.state_machine.push(MainMenuState(self))

    def run(self) -> None:
        """Main game loop — runs until ``self.running`` is False."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap to prevent spiral-of-death

            self.input.begin_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                self.input.handle_event(event)
                self.state_machine.handle_event(event)

            self.state_machine.update(dt)

            self.renderer.clear()
            self.state_machine.render(self.screen)

            if SHOW_FPS:
                fps_font = self.assets.get_font(16)
                fps_text = fps_font.render(
                    f"FPS: {self.clock.get_fps():.0f}", True, COLORS["text_dim"]
                )
                self.screen.blit(fps_text, (5, 5))

            pygame.display.flip()

            if self.state_machine.is_empty:
                self.running = False

        logger.info("Shutting down game engine...")
        pygame.quit()

    def quit(self) -> None:
        """Signal the game to exit after the current frame."""
        logger.info("Quit requested by state.")
        self.running = False
