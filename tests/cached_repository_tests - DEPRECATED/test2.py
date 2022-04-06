from repositories.cached_tracks_repository import CachedTracksRepository


def test_func2():
    print("Test 2 start")
    cr2 = CachedTracksRepository()
    print(cr2.get_tracks_by("album", None))
    print("Test 2 end")


