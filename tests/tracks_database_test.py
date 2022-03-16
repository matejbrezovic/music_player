import time

from repositories.tracks_repository import TracksRepository
from repositories.tracks_repository_json import TracksRepository as JSONTracksRepository


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

    # TracksRepository().reset_table("tracks")
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

# def test():
#     import sqlite3
#     conn = sqlite3.connect(DATABASE_PATH)
#
#     conn.create_function("strrev", 1, lambda s: s[::-1])
#
#     cur = conn.cursor()
#     cur.execute(r''' SELECT strrev('hello, world') ''')
#     cur.execute(r'''select file_path
#                 , strrev(
#                 SUBSTRING(strrev(file_path),
#                 INSTR(strrev(file_path), '/') + 1 ,
#                 INSTR('/',strrev(file_path),INSTR('/', strrev(file_path))+ 1) - INSTR('/', strrev(file_path)) -1)
#         )
#         from tracks''')
#     print(cur.fetchone()[0])  # dlrow ,olleh


if __name__ == '__main__':
    main()