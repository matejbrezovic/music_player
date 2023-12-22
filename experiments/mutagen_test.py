from mutagen.easyid3 import EasyID3

from repositories.tracks_repository import TracksRepository

if __name__ == "__main__":
    t = TracksRepository()
    root = "C:\\home\\matey\\Music\\"
    files = ["Nanatsu no Taizai OST - ELIEtheBEST.mp3",
             "My Hero Academia -You Say Run- (Orchestral Arrangement) - 10K SPECIAL.mp3",
             "Piano Orchestral 60 Minutes Version (With Relaxin - Alan Walker The Spectre - Piano Orchestral 60 Minu.mp3",
             "Lukas Graham - 7 Years Old.mp3"]

    file_paths = [root + file for file in files]

    tracks = t.convert_file_paths_to_tracks(file_paths)

    # for f, t in zip(file_paths, tracks):
    #     a = EasyID3(f)
    #     print(f)
    #     for key in EasyID3.valid_keys.keys():
    #         print(f"{key}:  {a.get(key)}")
    #     print("\n"*3)
    #
    # for track in tracks:
    #     print(f"{track.artist} ||| {track.title}")

