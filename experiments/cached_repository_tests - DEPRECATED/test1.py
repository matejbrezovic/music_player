from repositories.cached_tracks_repository import CachedTracksRepository


def test_func1():
    print("Test 1 start")
    cr = CachedTracksRepository()
    cr.cache_tracks()
    print(cr.get_tracks_by("album", None))
    print("Test 1 end")
