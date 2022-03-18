import music_tag as mt


def classify(module):
    return type(module.__name__, (),
                {key: staticmethod(value) if callable(value) else value
                 for key, value in ((name, getattr(module, name))
                                    for name in dir(module))})


class TagManager(classify(mt)):
    def __init__(self):
        super().__init__()

    # def get_tags(self):
    #     ...


if __name__ == '__main__':
    tm = TagManager()
    f = tm.load_file(r"C:\Users\matey\Music\Unknown Worlds\Subnautica\03 Ice in My Veins.mp3")
    print(f["title"])
