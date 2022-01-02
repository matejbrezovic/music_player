SUPPORTED_AUDIO_FORMATS = ["mp3", "m4a", "ogg"]

# Gui constants
import os

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

# Audio settings

FADE_IN_ANIM_KEY_VALUE = 0.04
FADE_IN_ANIM_START_VALUE = 0.05
FADE_OUT_ANIM_KEY_VALUE = FADE_IN_ANIM_KEY_VALUE
FADE_OUT_ANIM_END_VALUE = 0

# TRACKS = [DEFAULT_AUDIO_PATH + "/" + name for name in os.listdir(DEFAULT_AUDIO_PATH)]


# Database settings

DATABASE_PATH = os.path.abspath("database/test_database.db")


# Settings constants

DEFAULT_CONFIG_PATH = "C:/My Files/My Projects/music_player/settings/config.txt"
DEFAULT_LOADED_TRACKS_FILE_PATH = "C:/My Files/My Projects/music_player/settings/tracks.txt"

