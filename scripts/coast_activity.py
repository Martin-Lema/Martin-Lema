"""Render Martin Lema's public GitHub contribution calendar. Requires Python 3.9+ and gh."""
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[1]
LOGIN = "Martin-Lema"
QUERY = """query Calendar($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""
LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")
PALETTE = ("#333446", "#875052", "#c9714d", "#ffa74f", "#ffe29b")
HORIZON = '''<g fill="#373647">
  <path d="M0 48h124v-2h66v2h89v2H0zm360 2h79v-2h42v2h54v2H360zm443-3h103v-2h82v2h71v2H803zm220-14h48v-3h17v-3h21v-3h17v3h19v-2h15v3h22v-4h18v14h-177z"/>
  <path fill="#666073" d="M1044 34h40v-2h21v2h-18v2h-43zm84 4h30v2h-30z"/>
  <path fill="#d6a07d" d="M1127 17h3v9h-3zm-2-2h7v2h-7zm2-3h3v3h-3z"/>
</g>'''


def read_calendar(response, first, last):
    """GitHub can pad partial weeks. Keep exactly the requested dates."""
    if response.get("errors"):
        raise ValueError("GitHub returned an API error")
    user = response["data"]["user"]
    if user["login"].casefold() != LOGIN.casefold():
        raise ValueError("GitHub returned a different profile")
    days = {}
    calendar = user["contributionsCollection"]["contributionCalendar"]
    for week in calendar["weeks"]:
        for item in week["contributionDays"]:
            day = date.fromisoformat(item["date"])
            if not first <= day <= last:
                continue
            count = item["contributionCount"]
            level = LEVELS.index(item["contributionLevel"])
            if type(count) is not int or count < 0 or (count == 0) != (level == 0):
                raise ValueError(f"Invalid contribution count or level for {day}")
            if day in days:
                raise ValueError(f"Repeated calendar date {day}")
            days[day] = count, level
    if len(days) != (last - first).days + 1:
        raise ValueError(f"Incomplete contribution calendar for {first} through {last}")
    return dict(sorted(days.items()))


def fetch(first, last):
    command = [
        "gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={LOGIN}",
        "-f", f"from={first}T00:00:00Z", "-f", f"to={last}T23:59:59Z",
    ]
    payload = subprocess.check_output(command, text=True, timeout=60)
    return read_calendar(json.loads(payload), first, last)


def label(x, y, text, size, color="#c3b7b4", anchor="start", weight="400", mono=False):
    font = "ui-monospace,Menlo,Consolas,monospace" if mono else "Helvetica Neue,Arial,sans-serif"
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" '
            f'font-size="{size}" text-anchor="{anchor}" fill="{color}">{text}</text>')


def render(days, compact=False):
    width = 600 if compact else 1200
    left, right = (26, 574) if compact else (52, 1148)
    grid_x = left + (47 if compact else 52)
    first, last = min(days), max(days)
    sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = (last - sunday).days // 7 + 1
    rows = 2 if compact else 1
    split = (weeks + rows - 1) // rows
    column_pitch = (right - grid_x) / split
    pitch = int(column_pitch)
    cell = pitch - (3 if compact else 4)
    total = sum(count for count, _ in days.values())
    unit = "contribution" if total == 1 else "contributions"
    caption = f"{total:,} {unit}"
    period = f'{first:%d %b %Y} – {last:%d %b %Y}'
    out = []

    # Header and bottom border share the same inset as the calendar.
    if compact:
        out.append(label(left, 48, "GitHub activity", 37, "#ffe1b8", weight="600"))
        out.append(label(left, 82, caption, 22, "#ffb767"))
        top, stride = 133, 178
    else:
        out.append(label(left, 69, "GitHub activity", 42, "#ffe1b8", weight="600"))
        out.append(label(right, 64, caption, 26, "#ffb767", "end"))
        top, stride = 128, 0
    # Map the same 365 dates into one strip or two 6-month strips.
    for row in range(rows):
        y = top + row * stride
        labels = {}
        cells = []
        for day, (count, level) in days.items():
            column, weekday = divmod((day - sunday).days, 7)
            if column // split != row:
                continue
            local_column = column % split
            if day.day == 1:
                labels[local_column] = day.strftime("%b")
            x = grid_x + round(local_column * column_pitch)
            cell_y = y + weekday * pitch
            cells.append(f'<rect x="{x}" y="{cell_y}" width="{cell}" height="{cell}" fill="{PALETTE[level]}">'
                         f'<title>{day.isoformat()} · {count}</title></rect>')
        for column, month in labels.items():
            x = grid_x + round(column * column_pitch)
            # At a row boundary the end of a month name can extend past its cell.
            out.append(label(min(right - 31, x), y - 12, month, 17 if compact else 15, mono=True))
        for weekday, caption_day in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
            out.append(label(left, y + weekday * pitch + cell - 2, caption_day, 17 if compact else 15, mono=True))
        out.extend(cells)
    base = top + (rows - 1) * stride + 7 * pitch
    footer_y = base + 31
    out.append(label(left, footer_y, period, 16 if compact else 17, mono=True))
    # Show all five GitHub levels in the same order as the calendar.
    legend_x = right - 136
    out.append(label(legend_x - 9, footer_y, "Less", 15, anchor="end", mono=True))
    for level, color in enumerate(PALETTE):
        out.append(f'<rect x="{legend_x + 17 * level}" y="{footer_y - 12}" width="13" height="13" fill="{color}"/>')
    out.append(label(legend_x + 90, footer_y, "More", 15, mono=True))
    height = footer_y + 60
    out.append(f'<svg x="0" y="{height-53}" width="{width}" height="53" viewBox="0 0 1200 53" preserveAspectRatio="xMidYMax meet">')
    out.extend([HORIZON, "</svg>", "</svg>"])
    header = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{LOGIN} · GitHub activity</title>',
        f'<desc id="desc">{caption} from {first} through {last}. Each square is one day. Brighter squares indicate higher GitHub contribution levels.</desc>',
        f'<rect width="{width}" height="{height}" fill="#151521"/>',
    ]
    return "\n".join(header + out) + "\n"


def write_assets(days):
    for filename, compact in [("coast-activity.svg", False), ("coast-activity-mobile.svg", True)]:
        target = ROOT / "assets" / filename
        svg = render(days, compact)
        with NamedTemporaryFile(mode="w", dir=target.parent, encoding="utf-8", delete=False) as handle:
            handle.write(svg)
        Path(handle.name).replace(target)
        target.chmod(0o644)


if __name__ == "__main__":
    last = datetime.now(timezone.utc).date()
    first = last - timedelta(days=364)
    try:
        write_assets(fetch(first, last))
    except (ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        sys.exit(f"Could not refresh GitHub activity: {error}")
