import os

from PyQt6.QtGui import QColor

import utils

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

# Table views constants

SELECTION_QCOLOR = QColor(189, 232, 255)  # QColor(166, 223, 231)
SELECTION_QCOLOR_BORDER = QColor(110, 189, 232)  # QColor(100, 140, 200)
LOST_FOCUS_QCOLOR = QColor(0, 0, 0, 50)
LOST_FOCUS_QCOLOR_BORDER = QColor(0, 0, 0, 60)

# Audio controller style

DARK_AUDIO_CONTROLLER_COLOR = QColor("black")
LIGHT_AUDIO_CONTROLLER_COLOR = QColor("white")
DARK_AUDIO_CONTROLLER_HOVER_COLOR = QColor(80, 80, 80)
LIGHT_AUDIO_CONTROLLER_HOVER_COLOR = QColor(190, 190, 190)

LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND = QColor(170, 170, 170)
LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND = QColor(200, 200, 200)
LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_HANDLE_BACKGROUND = QColor("white")
DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND = QColor("lightGray")
DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND = QColor("darkGray")
DARK_AUDIO_CONTROLLER_SEEK_SLIDER_HANDLE_BACKGROUND = QColor("black")

MAIN_PANEL_COLUMN_NAMES = ("", "", "Artist", "Title", "Album", "Year", "Genre", "Rating", "Time")
MAIN_PANEL_VIEW_OPTIONS = ("Tracks", "Album and Tracks", "Album Covers", "Artists")
GROUP_OPTIONS = ("Album", "Artist", "Composer", "Folder", "Genre", "Year")

ROOT = utils.get_project_root(__file__)

# Database settings

DATABASE_PATH = os.path.join(ROOT, "database/test.db")

# Settings constants

DEFAULT_CONFIG_PATH = os.path.join(ROOT, "settings/config.txt")
DEFAULT_LOADED_TRACKS_FILE_PATH = os.path.join(ROOT, "settings/tracks.txt")
