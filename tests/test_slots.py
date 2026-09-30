from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from bot.slots import free_slots, overlaps, working_day

TZ = ZoneInfo("Asia/Tashkent")
DAY = date(2026, 10, 5)
OPENS, CLOSES = time(10, 0), time(20, 0)


def at(h, m=0, d=DAY):
    return datetime.combine(d, time(h, m), TZ)


def test_empty_day_has_all_slots_that_fit():
    slots = free_slots(DAY, 60, [], at(0), OPENS, CLOSES)
    assert slots[0] == at(10) and slots[-1] == at(19)
    assert len(slots) == 19


def test_busy_interval_blocks_overlapping_starts():
    slots = free_slots(DAY, 60, [(at(12), at(13))], at(0), OPENS, CLOSES)
    assert at(11, 30) not in slots and at(12) not in slots and at(12, 30) not in slots
    assert at(11) in slots and at(13) in slots


def test_long_service_does_not_run_past_closing():
    slots = free_slots(DAY, 150, [], at(0), OPENS, CLOSES)
    assert slots[-1] == at(17, 30)


def test_past_and_too_soon_slots_are_hidden():
    slots = free_slots(DAY, 30, [], at(14, 10), OPENS, CLOSES, lead_minutes=60)
    assert slots[0] == at(15, 30)


def test_overlaps_touching_intervals_are_free():
    assert not overlaps((at(10), at(11)), (at(11), at(12)))
    assert overlaps((at(10), at(11)), (at(10, 30), at(11, 30)))


def test_working_day_respects_weekly_and_single_days_off():
    assert not working_day(DAY, (0,), set())  # Monday
    assert not working_day(date(2026, 10, 6), (), {date(2026, 10, 6)})
    assert working_day(date(2026, 10, 7), (0,), set())
