import datetime


def get_formatted_time(track_duration: int) -> str:
    hours = int(track_duration / 3600000)
    minutes = int((track_duration / 60000) % 60)
    seconds = int((track_duration / 1000) % 60)

    return f'{str(hours) + ":" if hours else ""}{"0" + str(minutes) if hours else minutes}:' \
           f'{"0" + str(seconds) if seconds < 10 else seconds}'


def format_seconds(time_in_seconds: int) -> str:
    if not time_in_seconds:
        return "0:00"

    if time_in_seconds < 10:
        return f"0:0{time_in_seconds}"

    if time_in_seconds < 60:
        return f"0:{time_in_seconds}"
    time_str = "".join(str(datetime.timedelta(seconds=time_in_seconds))).lstrip("0:")

    return time_str


def get_formatted_time_in_mins(time_in_seconds: int) -> str:
    if not time_in_seconds:
        return "0:00"

    if time_in_seconds < 10:
        return f"0:0{time_in_seconds}"

    if time_in_seconds < 60:
        return f"0:{time_in_seconds}"

    mins = time_in_seconds // 60
    secs = time_in_seconds % 60

    if secs < 10:
        return f"{mins}:0{secs}"
    return f"{mins}:{secs}"


def format_player_position_to_seconds(position: int) -> int:
    return int(position / 1000)
