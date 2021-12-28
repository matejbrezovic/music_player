from tag_manager import TagManager


if __name__ == '__main__':
    tm = TagManager()

    file = tm.load_file("C:/Users/matey/Music/MobileMusic/Jonas Blue - Rise.mp3")
    print(file["Artist"])
