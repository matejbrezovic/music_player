from repositories.tracks_repository_database import TracksRepository
from repositories.tracks_repository import TracksRepository as JSONTracksRepository

# TODO sql injection



def main():
    tracks = JSONTracksRepository().get_tracks()

    rep = TracksRepository()
    for track in tracks:
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


if __name__ == '__main__':
    main()