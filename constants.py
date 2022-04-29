import os

from PyQt6.QtGui import QColor

import utils

APPLICATION_NAME = "Music Player"
APPLICATION_VERSION = "0.0.19"


SUPPORTED_AUDIO_FORMATS = {".mp3", ".m4a"}

# Gui constants

MAIN_WINDOW_X = 100
MAIN_WINDOW_Y = 100
MAIN_WINDOW_WIDTH = 1200
MAIN_WINDOW_HEIGHT = 800

MAIN_PANEL_MIN_WIDTH = 500
PANEL_MIN_WIDTH = 200

AUDIO_CONTROLLER_HEIGHT = 40

CONTROLLER_BUTTON_HEIGHT = 25
CONTROLLER_BUTTON_WIDTH = 25

STARTING_AUDIO_VOLUME = 30

# Table views constants

SELECTION_QCOLOR = QColor(0, 120, 215)  # QColor(189, 232, 255)  # QColor(166, 223, 231)
SELECTION_QCOLOR_BORDER = QColor(110, 189, 232)  # QColor(100, 140, 200)
LOST_FOCUS_QCOLOR = QColor(190, 204, 219)  # QColor(210, 210, 210)
LOST_FOCUS_QCOLOR_BORDER = QColor(180, 180, 180)

# Audio controller style

DARK_AUDIO_CONTROLLER_COLOR = QColor("black")
LIGHT_AUDIO_CONTROLLER_COLOR = QColor("white")
DARK_AUDIO_CONTROLLER_HOVER_COLOR = QColor(80, 80, 80)
LIGHT_AUDIO_CONTROLLER_HOVER_COLOR = QColor(190, 190, 190)

MAIN_PANEL_COLUMN_NAMES = ("", "", "Artist", "Title", "Album", "Year", "Genre", "Rating", "Time")
MAIN_PANEL_VIEW_OPTIONS = ("Tracks", "Album and Tracks", "Album Covers", "Artists")
GROUP_OPTIONS = ("Album", "Artist", "Composer", "Folder", "Genre", "Year")

ROOT = utils.get_project_root(__file__)

# Database constants

DATABASE_PATH = os.path.join(ROOT, "database/tracks_database.db")

# Settings constants

DEFAULT_CONFIG_PATH = os.path.join(ROOT, "settings/config.txt")
