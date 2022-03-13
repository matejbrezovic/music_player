import os
from collections import defaultdict

from PyQt6.QtGui import QColor

from utils import get_project_root

SUPPORTED_AUDIO_FORMATS = ["mp3", "m4a"]

# Gui constants

MAIN_WINDOW_X = 100
MAIN_WINDOW_Y = 100
MAIN_WINDOW_WIDTH = 1200
MAIN_WINDOW_HEIGHT = 800

MAIN_PANEL_MIN_WIDTH = 300
PANEL_MIN_WIDTH = 120

AUDIO_CONTROLLER_HEIGHT = 50

CONTROLLER_BUTTON_HEIGHT = 30
CONTROLLER_BUTTON_WIDTH = 30

STARTING_AUDIO_VOLUME = 50

DEFAULT_AUDIO_PATH = "/home/matey/Music"

# Table widgets constants

SELECTION_COLOR = "rgba(166, 223, 231, 0.8)"
LOST_FOCUS_COLOR = "rgba(0, 0, 0, 0.2)"
SELECTION_QCOLOR = QColor(156, 206, 233)  # QColor(166, 223, 231)
SELECTION_QCOLOR_BORDER = QColor(110, 189, 232)  # QColor(100, 140, 200)
LOST_FOCUS_QCOLOR = QColor(0, 0, 0, 50)
LOST_FOCUS_QCOLOR_BORDER = QColor(0, 0, 0, 60)


SELECTION_STYLESHEET = f"QTableView {{selection-background-color: {SELECTION_COLOR}; " \
                       f"selection-color: black; border: 0px; outline: 0}}"

LOST_FOCUS_STYLESHEET = f"QTableView {{selection-background-color: {LOST_FOCUS_COLOR}; " \
                        f"selection-color: black; border: 0px}}"

MAIN_PANEL_COLUMN_NAMES = ("", "", "Artist", "Title", "Album", "Year", "Genre", "Rating", "Time")
MAIN_PANAL_VIEW_OPTIONS = ("Tracks", "Album and Tracks", "Album Covers", "Artists")
GROUP_OPTIONS = ("Album", "Artist", "Composer", "Folder", "Genre", "Year")

# Audio settings

FADE_IN_ANIM_KEY_VALUE = 0.04
FADE_IN_ANIM_START_VALUE = 0.05
FADE_OUT_ANIM_KEY_VALUE = FADE_IN_ANIM_KEY_VALUE
FADE_OUT_ANIM_END_VALUE = 0

# TRACKS = [DEFAULT_AUDIO_PATH + "/" + name for name in os.listdir(DEFAULT_AUDIO_PATH)]

ROOT = get_project_root(__file__)

# Database settings

DATABASE_PATH = os.path.join(ROOT, "database/test.db")

# Settings constants

DEFAULT_CONFIG_PATH = os.path.join(ROOT, "settings/config.txt")
DEFAULT_LOADED_TRACKS_FILE_PATH = os.path.join(ROOT, "settings/tracks.txt")
