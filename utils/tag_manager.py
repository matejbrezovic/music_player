import music_tag as mt

from utils import classify


class TagManager(classify(mt)):  # todo DEPRECATED
    def __init__(self):
        super().__init__()

    # def get_tags(self):
    #     ...


if __name__ == '__main__':
    tm = TagManager()
    f = tm.load_file(r"C:\Users\matey\Music\Unknown Worlds\Subnautica\03 Ice in My Veins.mp3")
    print(f["title"])
