"""Pure scheduling logic, kept free of Telegram and DB so it is easy to test."""
from datetime import date, datetime, time, timedelta

Interval = tuple[datetime, datetime]


def overlaps(a: Interval, b: Interval) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def free_slots(day: date, minutes: int, busy: list[Interval], now: datetime,
               opens: time, closes: time, step: int = 30, lead_minutes: int = 60) -> list[datetime]:
    """Start times on `day` where a service of `minutes` fits between opening hours and busy intervals.

    `now` and all datetimes must share one timezone. Slots earlier than now + lead_minutes are skipped
    so a client cannot book a visit that starts in five minutes.
    """
    tz = now.tzinfo
    start = datetime.combine(day, opens, tz)
    end_of_day = datetime.combine(day, closes, tz)
    earliest = now + timedelta(minutes=lead_minutes)
    length = timedelta(minutes=minutes)
    result = []
    t = start
    while t + length <= end_of_day:
        slot = (t, t + length)
        if t >= earliest and not any(overlaps(slot, b) for b in busy):
            result.append(t)
        t += timedelta(minutes=step)
    return result


def working_day(day: date, weekly_off: tuple[int, ...], days_off: set[date]) -> bool:
    return day.weekday() not in weekly_off and day not in days_off
