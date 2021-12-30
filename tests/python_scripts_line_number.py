import os

file_counter = 0


def get_number_of_lines(file_path: str) -> int:
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for x in ["", "\n"]:
        while True:
            try: lines.remove(x)
            except ValueError: break

    return len(lines)


def get_number_of_lines_in_dir(dir_path: str):
    total = 0
    global file_counter
    for file in os.listdir(dir_path):
        full_path = dir_path + "/" + file
        if os.path.isdir(full_path):
            total += get_number_of_lines_in_dir(full_path)
        elif full_path.endswith(".py") and "tests" not in full_path:
            file_counter += 1
            total += get_number_of_lines(full_path)
    return total


if __name__ == "__main__":
    print(get_number_of_lines_in_dir("C:/My Files/My Projects/music_player"), f" lines in {file_counter} files")