import time

from repositories.tracks_repository import TracksRepository
from repositories.tracks_repository import TracksRepository as JSONTracksRepository

# TODO sql injection



def main():
    tracks = JSONTracksRepository().get_tracks()

    rep = TracksRepository()

    # rep.get_track_counts_grouped_by("artist")

    start = time.time()
    # tracks = rep.get_tracks_by("album", None)
    print(len(tracks))
    # rep.get_tracks_by()

    for track in tracks:
        print(track)
        rep.add_track(track)
    # rep.add_track(track)

    # got_track = rep.get_track_by_id(1)
    #
    # print(got_track)

    # for track in tracks:
    #     try:
    #         rep.add_track(track)
    #     except:
    #         pass
    # print(rep.get_all_tracks())
    # rep.get_tracks_grouped_by("album")

    print("Finished in:", time.time() - start)

if __name__ == '__main__':
    main()