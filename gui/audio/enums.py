from enum import Enum


class UserAction(Enum):
    Stopped = "stopped"
    Playing = "playing"
    Paused = "paused"


class RepeatMode(Enum):
    RepeatOn = "repeat_on"
    RepeatOff = "repeat_off"
    RepeatOne = "repeat_one"
