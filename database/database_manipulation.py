from repositories.cached_tracks_repository import CachedTracksRepository


def main():
    c = CachedTracksRepository()
    c.reset_table("tracks")
    # tracks = c.get_tracks()
    # for _ in range(20):
    #     c.add_tracks(tracks)


if __name__ == '__main__':
    main()
