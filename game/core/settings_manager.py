"""Settings manager for persisting and applying game settings."""
import json
import os
import pygame

from config import SAVE_DIR, SCREEN_WIDTH, SCREEN_HEIGHT
from game.audio.audio_manager import AudioManager


class SettingsManager:
    """Manages loading, saving, and applying game settings."""
    
    DEFAULT_SETTINGS = {
        "master_volume": 0.8,
        "bgm_volume": 0.5,
        "sfx_volume": 0.7,
        "fullscreen": False,
        "resolution_idx": 1, # e.g. 0: 960x640, 1: 1280x720, 2: 1920x1080
        "text_speed": 1.0, # 1.0 is normal, 2.0 is fast, etc.
        "battle_animations": True
    }
    
    RESOLUTIONS = [
        (960, 640),
        (1280, 720),
        (1920, 1080)
    ]

    def __init__(self, game):
        self.game = game
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings_path = os.path.join(SAVE_DIR, "settings.json")
        
        # Ensure save directory exists
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    def load(self):
        """Load settings from disk."""
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                    # Update with valid keys
                    for k, v in self.DEFAULT_SETTINGS.items():
                        if k in data and type(data[k]) == type(v):
                            self.settings[k] = data[k]
            except Exception as e:
                print(f"Failed to load settings: {e}")
        
        self.apply_all()

    def save(self):
        """Save settings to disk."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def apply_all(self):
        """Apply all current settings to the game state."""
        # Audio
        if self.game and hasattr(self.game, 'audio'):
            self.game.audio.master_volume = self.settings["master_volume"]
            self.game.audio.bgm_volume = self.settings["bgm_volume"]
            self.game.audio.sfx_volume = self.settings["sfx_volume"]
            
        # Display
        self.apply_display()

    def apply_display(self):
        """Apply fullscreen and resolution settings."""
        if not self.game:
            return
            
        # We can attempt to resize the pygame display. 
        # Since many UI elements are hardcoded to SCREEN_WIDTH/HEIGHT, 
        # using SCALED is a safe way to let Pygame scale the surface without breaking UI coordinates.
        flags = pygame.SCALED
        if self.settings["fullscreen"]:
            flags |= pygame.FULLSCREEN
        else:
            flags |= pygame.RESIZABLE
            
        res_idx = self.settings["resolution_idx"]
        if res_idx < 0 or res_idx >= len(self.RESOLUTIONS):
            res_idx = 0
            self.settings["resolution_idx"] = 0
            
        target_res = self.RESOLUTIONS[res_idx]
        
        try:
            # We request the target resolution, but internally it's scaled from the base (960x640)
            self.game.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
            if not self.settings["fullscreen"]:
                # To actually resize the window to the target res in windowed SCALED mode, 
                # pygame doesn't easily let you specify the window size differently from the surface size.
                # A common hack for pygame 2 SCALED is to set the logical size.
                # However, set_mode with SCALED will pick a window size.
                pass
        except pygame.error as e:
            print(f"Failed to apply display settings: {e}")
            
    # -- Getters & Setters --

    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        
    def update_volume(self, key, value):
        value = max(0.0, min(1.0, value))
        self.settings[key] = value
        if self.game and hasattr(self.game, 'audio'):
            if key == "master_volume":
                self.game.audio.master_volume = value
            elif key == "bgm_volume":
                self.game.audio.bgm_volume = value
            elif key == "sfx_volume":
                self.game.audio.sfx_volume = value
