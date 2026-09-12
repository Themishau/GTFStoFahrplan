import re

GTFS_TIME_PATTERN = r"[0-9]+:[0-5][0-9]:[0-5][0-9]"


def gtfs_time_to_seconds(value: str | None) -> int | None:
    """Seconds since the service day began, including hours >= 24.

    Empty optional times stay missing. Malformed nonempty times are rejected.
    """
    if value is None or value == "":
        return None
    if not re.fullmatch(GTFS_TIME_PATTERN, value):
        raise ValueError(f"Invalid GTFS time: {value!r}")
    hours, minutes, seconds = map(int, value.split(":"))
    return hours * 3600 + minutes * 60 + seconds
