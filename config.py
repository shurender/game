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
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

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
