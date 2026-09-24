"""Risu - Game Configuration."""
import os
import logging

# --- Display ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "Risu"

# --- Tiles ---
TILE_SIZE = 32

# --- Debug & Logging ---
DEBUG = False
SHOW_FPS = False
SHOW_COLLISIONS = False

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("risu")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_DIR = os.path.join(BASE_DIR, "saves")

# Asset Subdirectories
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SPRITES_DIR = os.path.join(IMAGES_DIR, "sprites")
SPRITESHEETS_DIR = os.path.join(IMAGES_DIR, "spritesheets")
TILES_DIR = os.path.join(IMAGES_DIR, "tiles")
CREATURES_DIR = os.path.join(IMAGES_DIR, "creatures")
ICONS_DIR = os.path.join(IMAGES_DIR, "icons")

SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
SFX_DIR = os.path.join(SOUNDS_DIR, "sfx")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
BGM_DIR = os.path.join(ASSETS_DIR, "audio", "bgm")

FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Standard audio templates and directory map
BGM_TEMPLATE = "assets/audio/bgm/{name}.ogg"

ASSET_DIRS = {
    "root": ASSETS_DIR,
    "images": IMAGES_DIR,
    "sprites": SPRITES_DIR,
    "spritesheets": SPRITESHEETS_DIR,
    "tiles": TILES_DIR,
    "creatures": CREATURES_DIR,
    "icons": ICONS_DIR,
    "sounds": SOUNDS_DIR,
    "sfx": SFX_DIR,
    "music": MUSIC_DIR,
    "bgm": BGM_DIR,
    "fonts": FONTS_DIR,
}

# --- Colors ---
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "bg_dark": (15, 12, 25),
    "bg_medium": (25, 20, 45),
    "accent": (120, 200, 255),
    "accent_warm": (255, 160, 80),
    "accent_green": (100, 220, 140),
    "text": (230, 230, 240),
    "text_dim": (140, 135, 160),
    "hp_green": (80, 200, 120),
    "hp_yellow": (240, 200, 60),
    "hp_red": (220, 60, 60),
    "menu_bg": (20, 18, 35),
    "menu_border": (80, 70, 120),
    "menu_highlight": (60, 50, 100),
}
