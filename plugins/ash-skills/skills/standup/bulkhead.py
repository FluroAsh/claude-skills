#!/usr/bin/env python3
"""Render the standup sprint bulkhead.

Usage:
  bulkhead.py <<'JSON'
  {"name": "Team Sprint 22", "start": "2026-11-10T23:00:00.000Z",
   "end": "2026-11-23T14:00:00.000Z", "counts": [["To Do", 2], ["In Progress", 3]]}
  JSON
  bulkhead.py --test

Input is JSON on stdin so Jira text never passes through the shell. Optional
"today": "YYYY-MM-DD". Sprint dates are Jira ISO timestamps, converted to the
local timezone before taking the date. Counts are in display order; zero
counts are dropped.
"""
import datetime as dt
import json
import sys

LABELS = {"pending deploy": "Deploy"}
RULE = "─" * 52


def clean(text):
    """Jira text is untrusted: keep it on one line and unable to close the code fence."""
    return " ".join(str(text).replace("`", "'").split())


def local_date(iso):
    iso = iso.strip().replace("Z", "+00:00")
    # Jira sends +1000 without a colon, which fromisoformat rejects before 3.11.
    if len(iso) > 5 and iso[-5] in "+-" and iso[-3] != ":":
        iso = iso[:-2] + ":" + iso[-2:]
    parsed = dt.datetime.fromisoformat(iso)
    if parsed.tzinfo is None:
        return parsed.date()
    return parsed.astimezone().date()


def workdays_after(today, last):
    n, day = 0, today + dt.timedelta(days=1)
    while day <= last:
        n += day.weekday() < 5
        day += dt.timedelta(days=1)
    return n


def render(name, start, end, counts, today):
    left = workdays_after(today, end)
    lines = [
        f"{clean(name).upper()} · {today:%a} {today.day} {today:%b} · {left} day{'s' if left != 1 else ''} left",
        RULE,
    ]
    monday = today - dt.timedelta(days=today.weekday())
    week = [monday + dt.timedelta(days=i) for i in range(5)]
    labels, marks = [], []
    for day in week:
        if day == end:
            mark = "⚑"
        elif day < start or day > end:
            mark = "·"
        elif day < today:
            mark = "●"
        elif day == today:
            mark = "◉"
        else:
            mark = "○"
        labels.append(f"{day:%a}")
        marks.append(mark)
    label_row = "  ".join(labels)
    mark_row = " " + "────".join(marks)
    if end > week[-1]:
        flag_label = f"{end:%a}" if (end - week[-1]).days < 7 else f"{end:%a} {end.day} {end:%b}"
        # 7 spaces puts the label's middle letter over ⚑, like the day labels.
        label_row += " " * 7 + flag_label
        mark_row += "╌" * 9 + "⚑ sprint ends"
    lines += [label_row, mark_row, RULE]
    shown = [f"{LABELS.get(clean(s).lower(), clean(s))} {n}" for s, n in counts if n > 0]
    if shown:
        lines.append(" │ ".join(shown))
    return "\n".join(lines)


def test():
    start, end = dt.date(2026, 11, 11), dt.date(2026, 11, 24)
    counts = [("Open", 2), ("In progress", 3), ("QA", 1), ("Pending Deploy", 1), ("Blocked", 0), ("Done", 2)]
    mid = render("Helios Sprint 22", start, end, counts, dt.date(2026, 11, 19)).split("\n")
    assert mid[0] == "HELIOS SPRINT 22 · Thu 19 Nov · 3 days left", mid[0]
    assert mid[2] == "Mon  Tue  Wed  Thu  Fri       Tue", mid[2]
    assert mid[3] == " ●────●────●────◉────○╌╌╌╌╌╌╌╌╌⚑ sprint ends", mid[3]
    assert mid[5] == "Open 2 │ In progress 3 │ QA 1 │ Deploy 1 │ Done 2", mid[5]
    assert mid[3].index("⚑") == mid[2].rindex("T") + 1, "flag under its label"
    early = render("Helios Sprint 22", dt.date(2026, 11, 18), end, counts, dt.date(2026, 11, 19)).split("\n")
    assert early[3].startswith(" ·────·────●────◉"), early[3]  # days before the start are not done
    last = render("Helios Sprint 22", start, end, counts, end).split("\n")
    assert last[0].endswith("0 days left"), last[0]
    assert last[3] == " ●────⚑────·────·────·", last[3]
    assert workdays_after(dt.date(2026, 11, 20), dt.date(2026, 11, 23)) == 1  # Fri → Mon skips the weekend
    stamp = dt.datetime(2026, 11, 19, 10, tzinfo=dt.timezone(dt.timedelta(hours=11)))
    assert local_date("2026-11-19T10:00:00.000+1100") == stamp.astimezone().date()
    assert clean("Sprint\n```\n[x](y)") == "Sprint ''' [x](y)"
    print("ok")


def main():
    if sys.argv[1:] == ["--test"]:
        return test()
    data = json.load(sys.stdin)
    if not data.get("start") or not data.get("end"):
        sys.exit("bulkhead: the sprint has no start or end date")
    counts = [(s, int(n)) for s, n in data.get("counts", [])]
    today = dt.date.fromisoformat(data["today"]) if data.get("today") else dt.date.today()
    print(render(data.get("name", "Sprint"), local_date(data["start"]), local_date(data["end"]), counts, today))


if __name__ == "__main__":
    main()
