from repositories.cached_tracks_repository import CachedTracksRepository


def main():
    c = CachedTracksRepository()
    c.reset_table("tracks")


if __name__ == '__main__':
    main()
