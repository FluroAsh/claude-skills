#!/usr/bin/env python3
"""Render a progress review (day or week) as one self-contained HTML file, and prune old ones.

Usage:
  render.py < report.json      prints the path of the written file
  render.py --prune-only       only prune

Input is JSON on stdin (see SKILL.md, "Report data"), so Slack, Jira and
GitHub text never passes through the shell. All text is HTML-escaped; the only
markup allowed in text fields is **bold** and [label](https://link).

Layout: header and tally, the read, a "shape of the day" strip (one row per
day in week mode) whose dots jump to the matching moment, the replay (every
moment in time order), takeaways, first thing next, promises in flight, then
optional week sections and the question to sit with. Achievement-worthy
wins carry a star.

Files go to $ASH_PROGRESS_DIR, else $XDG_CACHE_HOME/ash-skills/progress, else
~/.cache/ash-skills/progress. Every run deletes daily reports from before
today and weekly reports older than seven days.
"""
import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

KINDS = {  # label, strip dot shown
    "win": ("Win", True),
    "good": ("Good call", True),
    "fine": ("Fine", True),
    "miss": ("Missed", True),
    "signal": ("Signal", True),
    "plan": ("Plan", False),
}
PROMISE = {"kept": "Kept", "open": "Open", "risk": "At risk", "broken": "Broken"}
LEVER_STATE = {"strong": "At the bar", "mixed": "Mixed", "missed": "Missed chance", "quiet": "Quiet"}


# ---------------------------------------------------------------- files
def out_dir():
    if os.environ.get("ASH_PROGRESS_DIR"):
        return Path(os.environ["ASH_PROGRESS_DIR"]).expanduser()
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "ash-skills" / "progress"


def prune(folder, today):
    removed = []
    for f in folder.glob("progress-*.html"):
        m = re.fullmatch(r"progress-(day|week)-(\d{4}-\d{2}-\d{2})\.html", f.name)
        if not m:
            continue
        day = dt.date.fromisoformat(m.group(2))
        if (m.group(1) == "day" and day < today) or (m.group(1) == "week" and (today - day).days > 7):
            f.unlink()
            removed.append(f.name)
    return removed


# ---------------------------------------------------------------- helpers
def md(text):
    """Escape, then allow **bold** and https links only."""
    s = html.escape(str(text or ""), quote=True)
    s = re.sub(r"\[([^\]]+)\]\((https://[^\s)]+)\)",
               lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def esc(text):
    return html.escape(str(text or ""), quote=True)


def mins(hhmm):
    h, m = str(hhmm).split(":")
    return int(h) * 60 + int(m)


def t12(hhmm):
    h, m = divmod(mins(hhmm), 60)
    return f"{h % 12 or 12}:{m:02d}{'am' if h < 12 else 'pm'}"


def day_label(iso, short=False):
    d = dt.date.fromisoformat(iso)
    return f"{d:%a} {d.day}" if short else f"{d:%a} {d.day} {d:%b}"


def kind_of(m):
    return m.get("kind") if m.get("kind") in KINDS else "fine"


# ---------------------------------------------------------------- sections
def header(r, week):
    chips = "".join(f'<span class="chip">{md(c)}</span>' for c in r.get("context", []))
    sub = ""
    if week and r.get("window"):
        sub = f'<p class="sub">{day_label(r["window"]["start"])} to {day_label(r["window"]["end"])}</p>'
    moments = r.get("moments", [])
    n = lambda k: sum(1 for m in moments if kind_of(m) == k)
    blocks = r.get("blocks", [])
    done = sum(1 for b in blocks if b.get("status") == "done")
    tiles = [(n("win"), "wins", "good"), (n("good"), "good calls", "good"), (n("miss"), "missed chances", "bad")]
    tally = "".join(f'<div><b class="v-{c}">{v}</b>{l}</div>' for v, l, c in tiles if v)
    if blocks:
        tally += f'<div><b>{len(blocks)}</b>planned blocks, {done} done</div>'
    return (f'<header><p class="eyebrow">{"Week" if week else "Day"} review</p><h1>{md(r.get("title", ""))}</h1>{sub}'
            f'<div class="chips">{chips}</div><div class="tally">{tally}</div></header>')


def strip(r, week):
    moments = [m for m in r.get("moments", []) if KINDS[kind_of(m)][1]]
    blocks = r.get("blocks", [])
    if not moments and not blocks:
        return ""
    times = [mins(m["time"]) for m in moments] + [mins(b[k]) for b in blocks for k in ("start", "end")]
    lo = max(7 * 60, min(min(times) // 60 * 60, 9 * 60))
    hi = min(20 * 60, max(-(-max(times) // 60) * 60, 17 * 60))
    outside = [f'{t12(b["start"])}–{t12(b["end"])} {b.get("title", "")}'.strip() for b in blocks
               if mins(b["end"]) <= lo or mins(b["start"]) >= hi]
    outside += [f'{t12(m["time"])} {KINDS[kind_of(m)][0].lower()}' for m in moments if not lo <= mins(m["time"]) <= hi]
    pos = lambda t: (min(max(t, lo), hi) - lo) / (hi - lo) * 100
    days = sorted({m.get("day", "") for m in moments} | {b.get("day", "") for b in blocks}) if week else [""]
    rows = []
    for day in days:
        blk = "".join(
            f'<div class="s-blk" style="left:{pos(mins(b["start"])):.1f}%;width:{max(pos(mins(b["end"])) - pos(mins(b["start"])), .8):.1f}%" '
            f'title="{esc(t12(b["start"]))}–{esc(t12(b["end"]))} · {esc(b.get("title", ""))}"></div>'
            for b in blocks if not week or b.get("day") == day)
        pins = "".join(
            f'<a class="s-pin k-{kind_of(m)}" href="#m{i}" style="left:{pos(mins(m["time"])):.1f}%" '
            f'title="{esc(t12(m["time"]))} · {KINDS[kind_of(m)][0]}"></a>'
            for i, m in enumerate(r.get("moments", []))
            if KINDS[kind_of(m)][1] and (not week or m.get("day") == day) and lo <= mins(m["time"]) <= hi)
        label = f'<span class="s-day">{day_label(day, short=True)}</span>' if week else ""
        rows.append(f'<div class="s-row">{label}<div class="s-strip"><div class="s-axis"></div>{blk}{pins}</div></div>')
    ticks = "".join(f'<span style="left:{pos(h * 60):.1f}%">{h % 12 or 12}{"am" if h < 12 else "pm"}</span>' for h in range(-(-lo // 180) * 3, hi // 60 + 1, 3))
    legend = "".join(f'<span><i class="k-{k}"></i>{KINDS[k][0]}</span>' for k in ("win", "good", "fine", "miss", "signal"))
    note = f'<span class="s-out">Outside {t12(f"{lo // 60}:00")}–{t12(f"{hi // 60}:00")}: {esc(", ".join(outside))}</span>' if outside else ""
    return (f'<section class="card s-card"><p class="eyebrow">Shape of the {"week" if week else "day"}</p>{"".join(rows)}'
            f'<div class="s-row">{"<span class=s-day></span>" if week else ""}<div class="s-ticks">{ticks}</div></div>'
            f'<div class="s-legend">{legend}<span><i class="k-blk"></i>Planned block</span>{note}</div></section>')


def replay(r, week):
    out, last_day = [], None
    for i, m in enumerate(r.get("moments", [])):
        k = kind_of(m)
        if week and k not in ("win", "miss", "signal"):
            continue
        if week and m.get("day") != last_day:
            last_day = m.get("day")
            out.append(f'<div class="dayhead">{day_label(last_day)}</div>')
        star = '<span class="star" title="Achievement-worthy">★</span>' if m.get("keep") else ""
        tag = "" if k == "plan" else f'<span class="k">{KINDS[k][0]}{" · " + esc(m["lever"]) if m.get("lever") else ""}</span>{star}'
        out.append(f'<div id="m{i}" class="m m-{k}"><span class="t">{t12(m["time"])}</span><span class="dot"></span>'
                   f'<div class="body">{tag}{md(m.get("text", ""))}</div></div>')
    return f'<div class="tape">{"".join(out)}</div>' if out else ""


def takeaways(r):
    t = r.get("takeaways") or {}
    cards = "".join(f'<div><h3>{lab}</h3><p>{md(t[key])}</p></div>'
                    for key, lab in (("keep", "Keep doing"), ("start", "Start doing"), ("watch", "Watch")) if t.get(key))
    return f'<section class="card"><h2>Takeaways</h2><div class="take">{cards}</div></section>' if cards else ""


def next_move(r, week):
    nm = r.get("next_move")
    if not nm:
        return ""
    second = f'<p class="second"><strong>Then:</strong> {md(nm["second"])}</p>' if nm.get("second") else ""
    return (f'<section class="card next"><p class="eyebrow">{"Focus for the rest of the week" if week else nm.get("label", "First thing next")}</p>'
            f'<h2>{md(nm["action"])}</h2><p>{md(nm.get("why", ""))}</p>{second}</section>')


def promises(r):
    rows = "".join(
        f'<tr><td>{md(p.get("to"))}</td><td>{md(p.get("said"))}</td>'
        f'<td><span class="pill p-{esc(p.get("state", "open"))}">{PROMISE.get(p.get("state"), "Open")}</span></td><td class="muted">{md(p.get("note", ""))}</td></tr>'
        for p in r.get("promises", []))
    return (f'<section class="card"><h2>Promises in flight</h2><div class="scroll"><table><thead><tr><th>To</th><th>You said</th>'
            f'<th>State</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table></div></section>') if rows else ""


def week_sections(r):
    parts = []
    if r.get("lever_days"):
        days = sorted({d for v in r["lever_days"].values() for d in v})
        head = "".join(f"<th>{day_label(d, short=True)}</th>" for d in days)
        body = "".join(
            f'<tr><th>{md(name)}</th>' + "".join(
                f'<td><span class="cell l-{esc(v.get(d, "quiet"))}" title="{LEVER_STATE.get(v.get(d, "quiet"), "")}"></span></td>' for d in days) + "</tr>"
            for name, v in r["lever_days"].items())
        parts.append(f'<section class="card"><h2>Levers by day</h2><div class="scroll"><table class="heat"><thead><tr><th></th>{head}</tr></thead>'
                     f'<tbody>{body}</tbody></table></div></section>')
    if r.get("trends"):
        tiles = "".join(f'<div class="tile"><b>{md(t["value"])}</b><span class="tl">{md(t["label"])}</span><span class="muted">{md(t.get("note", ""))}</span></div>'
                        for t in r["trends"])
        parts.append(f'<section class="card"><h2>Trends</h2><div class="tiles">{tiles}</div></section>')
    if r.get("summary"):
        cols = "".join(f'<div><h3>{md(k)}</h3><ul>{"".join(f"<li>{md(x)}</li>" for x in v)}</ul></div>' for k, v in r["summary"].items() if v)
        parts.append(f'<section class="card"><h2>The week so far</h2><div class="cols">{cols}</div></section>')
    return "".join(parts)


def extras(r):
    parts = []
    if r.get("question"):
        parts.append(f'<section class="card"><h2>A question to sit with</h2><p class="q">{md(r["question"])}</p></section>')
    if r.get("reference"):
        parts.append(f'<footer><strong>Reference note:</strong> {md(r["reference"])}</footer>')
    return "".join(parts)


def render(r):
    week = r.get("mode") == "week"
    read = f'<section class="card read"><p class="eyebrow">The read</p><p>{md(r["read"])}</p></section>' if r.get("read") else ""
    body = (header(r, week) + read + strip(r, week) + replay(r, week) + takeaways(r) + next_move(r, week)
            + promises(r) + (week_sections(r) if week else "") + extras(r))
    title = f'{"Week" if week else "Day"} Review · {esc(r.get("title", ""))}'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>')


CSS = """
:root{--bg:#f7f6f3;--card:#fff;--ink:#1c1c1e;--muted:#6b6b72;--line:#e5e3dd;--accent:#3b5bdb;
--good:#2b8a3e;--good-bg:#e7f5ea;--fine:#b7791f;--fine-bg:#fdf3e1;--bad:#c92a2a;--bad-bg:#fff0f0;
--sig:#5c7cfa;--sig-bg:#eef2ff;--quiet:#868e96;--quiet-bg:#f1f3f5;--soft:#fbf7ec}
@media (prefers-color-scheme:dark){:root{--bg:#121214;--card:#1c1c20;--ink:#ececef;--muted:#9b9ba3;--line:#2d2d33;--accent:#91a7ff;
--good:#69db7c;--good-bg:#1b3022;--fine:#f6c453;--fine-bg:#33291a;--bad:#ff8787;--bad-bg:#3a1d1d;--sig:#91a7ff;--sig-bg:#1f2440;
--quiet:#adb5bd;--quiet-bg:#25252a;--soft:#24221a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}
a{color:var(--accent)}main{max-width:900px;margin:0 auto;padding:32px 16px 72px}
.eyebrow{text-transform:uppercase;letter-spacing:.09em;font-size:11px;font-weight:700;color:var(--muted);margin:0 0 6px}
h1{font-size:30px;line-height:1.2;margin:0 0 8px;letter-spacing:-.015em}h2{font-size:17px;margin:0 0 12px}h3{font-size:15px;margin:0 0 6px}
.sub,.muted{color:var(--muted)}.sub{margin:0 0 6px}
.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:2px 10px;font-size:13px}
.tally{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 0}.tally div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 14px;font-size:13px}
.tally b{font-size:22px;margin-right:6px}.v-good{color:var(--good)}.v-bad{color:var(--bad)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-top:16px}
.read{background:var(--soft)}.read p:last-child{margin:0;font-size:17px}
.next{border:2px solid var(--accent)}.next h2{margin-bottom:6px}.next p{margin:0 0 4px}.second{color:var(--muted)}
.s-card{padding:16px 22px 14px}.s-row{display:flex;align-items:center;gap:10px}.s-day{width:44px;flex:none;font-size:12px;color:var(--muted)}
.s-strip{position:relative;height:34px;margin:0 8px;flex:1}.s-ticks{position:relative;height:18px;margin:0 8px;flex:1}
.s-axis{position:absolute;left:0;right:0;top:15px;height:4px;border-radius:2px;background:var(--line)}
.s-blk{position:absolute;top:11px;height:12px;border-radius:4px;background:var(--quiet-bg);border:1px solid var(--line)}
.s-pin{position:absolute;top:10px;width:14px;height:14px;margin-left:-7px;border-radius:50%;border:2px solid var(--card);display:block}
.s-pin:hover{transform:scale(1.3)}
.s-ticks span{position:absolute;font-size:11px;color:var(--muted);transform:translateX(-50%)}
.k-win{background:var(--good)}.k-good{background:var(--good);opacity:.45}.k-fine{background:var(--fine)}.k-miss{background:var(--bad)}.k-signal{background:var(--sig)}
.s-legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:var(--muted);margin-top:6px}
.s-legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.s-legend i.k-blk{border-radius:2px;background:var(--quiet-bg);border:1px solid var(--line)}.s-out{margin-left:auto}
.tape{position:relative;margin-top:20px;padding-left:96px}
.tape:before{content:"";position:absolute;left:84px;top:6px;bottom:6px;width:2px;background:var(--line)}
.dayhead{margin:18px 0 8px -96px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.m{position:relative;margin:0 0 10px;scroll-margin-top:16px}
.m .t{position:absolute;left:-96px;width:72px;text-align:right;font-size:12px;color:var(--muted);top:11px;font-variant-numeric:tabular-nums}
.m .dot{position:absolute;left:-18px;top:13px;width:12px;height:12px;border-radius:50%;background:var(--card);border:2px solid var(--quiet)}
.m .body{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 14px}
.m .k{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-right:8px}
.m-win .dot{background:var(--good);border-color:var(--good)}.m-win .body{border-color:var(--good);background:var(--good-bg)}.m-win .k{color:var(--good)}
.m-good .dot{border-color:var(--good)}.m-good .k{color:var(--good)}
.m-fine .dot{border-color:var(--fine)}.m-fine .k{color:var(--fine)}
.m-miss .dot{background:var(--bad);border-color:var(--bad)}.m-miss .body{border-left:4px solid var(--bad)}.m-miss .k{color:var(--bad)}
.m-signal .dot{border-color:var(--sig)}.m-signal .body{background:var(--sig-bg);font-size:14px}.m-signal .k{color:var(--sig)}
.m-plan .body{background:transparent;border-style:dashed;color:var(--muted);font-size:13px;padding:5px 12px}.m-plan .dot{width:8px;height:8px;left:-16px;top:11px}
.m:target .body{outline:2px solid var(--accent)}
.take{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.take div{border:1px solid var(--line);border-radius:12px;padding:12px 14px}.take p{margin:0}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:8px 10px;border-top:1px solid var(--line)}
thead th{border-top:0;font-size:12px;color:var(--muted);font-weight:600}.scroll{overflow-x:auto}
.pill{display:inline-block;border-radius:999px;padding:1px 9px;font-size:12px;font-weight:700;white-space:nowrap}
.p-kept{background:var(--good-bg);color:var(--good)}.p-open{background:var(--quiet-bg);color:var(--quiet)}.p-risk,.p-broken{background:var(--bad-bg);color:var(--bad)}
.heat{width:auto}.heat td,.heat th{text-align:center;padding:4px 8px}.heat tbody th{text-align:left;font-weight:500}
.cell{display:inline-block;width:14px;height:14px;border-radius:4px;background:var(--quiet-bg)}
.cell.l-strong{background:var(--good)}.cell.l-mixed{background:var(--fine)}.cell.l-missed{background:var(--bad)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}.tile{border:1px solid var(--line);border-radius:10px;padding:10px 12px;display:grid}
.tile b{font-size:22px}.tile .tl{font-weight:600}.tile .muted{font-size:13px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
ul{margin:0;padding-left:18px}li{margin:4px 0}
.tag{display:inline-block;font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:0 8px;margin-left:4px}
.q{margin:0;font-style:italic}.star{color:var(--fine);margin-right:6px}footer{color:var(--muted);font-size:13px;padding:16px 4px 0}
@media(max-width:640px){.tape{padding-left:22px}.tape:before{left:10px}.dayhead{margin-left:-22px}
.m .t{position:static;text-align:left;display:block;margin-bottom:2px;width:auto}.m .dot{left:-18px;top:30px}.s-out{margin-left:0}h1{font-size:24px}}
"""


def main():
    today = dt.date.today()
    folder = out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    removed = prune(folder, today)
    if "--prune-only" in sys.argv:
        print(f"pruned {len(removed)} file(s)")
        return
    report = json.load(sys.stdin)
    mode = "week" if report.get("mode") == "week" else "day"
    path = folder / f"progress-{mode}-{today.isoformat()}.html"
    path.write_text(render(report), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
