from dataclasses import dataclass


@dataclass
class Track:
    track_id: int
    name: str
    album: str
    artist: str
    composer: str
    genre: str
    artwork_path: str

