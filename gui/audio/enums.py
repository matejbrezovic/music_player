from enum import Enum


class AudioUserAction(Enum):
    Stopped = "stopped"
    Playing = "playing"
    Paused = "paused"


class AudioRepeatMode(Enum):
    RepeatOn = "repeat_on"
    RepeatOff = "repeat_off"
    RepeatOne = "repeat_one"
