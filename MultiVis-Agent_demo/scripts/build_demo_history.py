#!/usr/bin/env python3
"""Build demo history.json (4 items) and ensure chart PNGs exist.

The history shipped with the desktop demo should look impressive out of
the box: every entry must have a chart preview, a meaningful SQL query,
and realistic Altair code so the user can replay a session and see a
fully-rendered, well-documented chart side-by-side with its source.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "history"
CHART_JSON = HISTORY / "chart_json"
CHART_RESULT = HISTORY / "chart_result"
INPUT_DIR = HISTORY / "input"


def _inline_external_data(vega: dict) -> dict:
    """Inline any external URL data so vl_convert can render offline."""
    data = vega.get("data") or {}
    url = data.get("url")
    if not url:
        return vega
    candidate = ROOT / url.lstrip("/")
    if not candidate.exists():
        return vega
    try:
        values = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception:
        return vega
    vega["data"] = {"values": values}
    return vega


def _ensure_png(n: int) -> None:
    png = CHART_RESULT / f"{n}.png"
    vega = CHART_JSON / f"{n}.vega.json"
    if not vega.exists():
        return
    # Re-render when the existing PNG is suspiciously small (broken chart).
    if png.exists() and png.stat().st_size > 5000:
        return
    try:
        import vl_convert as vlc
    except ImportError:
        return
    vega_dict = json.loads(vega.read_text(encoding="utf-8"))
    vega_dict = _inline_external_data(vega_dict)
    vega.write_text(json.dumps(vega_dict, ensure_ascii=False), encoding="utf-8")
    png.write_bytes(vlc.vegalite_to_png(vega.read_text(encoding="utf-8"), scale=2))


STACKED_BAR_CODE = """\
# Stacked bar chart — Activity participants by role
import altair as alt
import pandas as pd
import sqlite3

con = sqlite3.connect('database/activity_1.sqlite')
faculty = pd.read_sql_query(
    \"\"\"
    SELECT a.activity_name,
           'Faculty' AS participant_type,
           COUNT(*) AS participant_count
    FROM Faculty_Participates_in fp
    JOIN Activity a ON a.actid = fp.actid
    GROUP BY a.activity_name
    \"\"\",
    con,
)
students = pd.read_sql_query(
    \"\"\"
    SELECT a.activity_name,
           'Student' AS participant_type,
           COUNT(*) AS participant_count
    FROM Participates_in p
    JOIN Activity a ON a.actid = p.actid
    GROUP BY a.activity_name
    \"\"\",
    con,
)
df = pd.concat([students, faculty], ignore_index=True)

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X('activity_name:N', title='Activity'),
        y=alt.Y('participant_count:Q', title='Number of Participants'),
        color=alt.Color('participant_type:N', title='Participant Type'),
        order=alt.Order('participant_type:N', sort='descending'),
    )
    .properties(
        title='Number of Students and Faculty Participating in Each Activity'
    )
)
chart
"""

SCATTER_CODE = """\
# Reference-matched scatter plot — Average student age per activity
import altair as alt
import pandas as pd
import sqlite3

con = sqlite3.connect('database/activity_1.sqlite')
df = pd.read_sql_query(
    \"\"\"
    SELECT a.activity_name,
           AVG(s.age) AS avg_age
    FROM Participates_in p
    JOIN Student s ON s.StuID = p.StuID
    JOIN Activity a ON a.actid = p.actid
    GROUP BY a.activity_name
    \"\"\",
    con,
)
overall = df['avg_age'].mean()
df['delta'] = df['avg_age'] - overall

chart = (
    alt.Chart(df)
    .mark_circle(size=120)
    .encode(
        x=alt.X('activity_name:N', title='Activity', sort='-y'),
        y=alt.Y('avg_age:Q', title='Average Age', scale=alt.Scale(zero=False)),
        color=alt.Color(
            'delta:Q',
            scale=alt.Scale(scheme='redblue', domainMid=0),
            title='Δ vs Overall',
        ),
        tooltip=['activity_name', 'avg_age', 'delta'],
    )
    .properties(title='Average Student Age per Activity (vs Overall Average)')
)
chart
"""

PIE_CODE = """\
# Pie chart — Track counts per music genre
import altair as alt
import pandas as pd
import sqlite3

con = sqlite3.connect('database/chinook_1.sqlite')
df = pd.read_sql_query(
    \"\"\"
    SELECT g.Name AS genre, COUNT(t.TrackId) AS tracks
    FROM Track t
    JOIN Genre g ON g.GenreId = t.GenreId
    GROUP BY g.Name
    ORDER BY tracks DESC
    \"\"\",
    con,
)

chart = (
    alt.Chart(df)
    .mark_arc(innerRadius=40)
    .encode(
        theta=alt.Theta('tracks:Q', stack=True),
        color=alt.Color('genre:N', scale=alt.Scale(scheme='tableau20'), title='Genre'),
        order=alt.Order('tracks:Q', sort='descending'),
        tooltip=['genre', 'tracks'],
    )
    .properties(title='Track Count by Music Genre (Chinook)')
)
chart
"""

REFINED_SCATTER_CODE = """\
# Refined scatter — rotated labels, grid, hollow points
import altair as alt
import pandas as pd
import sqlite3

con = sqlite3.connect('database/activity_1.sqlite')
df = pd.read_sql_query(
    \"\"\"
    SELECT a.activity_name,
           AVG(s.age) AS avg_age
    FROM Participates_in p
    JOIN Student s ON s.StuID = p.StuID
    JOIN Activity a ON a.actid = p.actid
    GROUP BY a.activity_name
    \"\"\",
    con,
)
overall = df['avg_age'].mean()
df['delta'] = df['avg_age'] - overall

chart = (
    alt.Chart(df)
    .mark_point(size=180, filled=False, strokeWidth=2.2)
    .encode(
        x=alt.X(
            'activity_name:N',
            title='Activity',
            sort='-y',
            axis=alt.Axis(labelAngle=-35, labelLimit=200),
        ),
        y=alt.Y(
            'avg_age:Q',
            title='Average Age',
            scale=alt.Scale(zero=False),
            axis=alt.Axis(grid=True, gridDash=[2, 2], gridOpacity=0.5),
        ),
        color=alt.Color(
            'delta:Q',
            scale=alt.Scale(scheme='redblue', domainMid=0),
            title='Δ vs Overall',
        ),
        tooltip=['activity_name', 'avg_age', 'delta'],
    )
    .properties(
        title='Average Student Age per Activity — Refined View',
        width='container',
        height=380,
    )
)
chart
"""


def build() -> None:
    for n in (1, 2, 3, 4):
        _ensure_png(n)

    items = [
        {
            "db_name": "activity_1.sqlite",
            "query": (
                "Create a stacked bar chart showing the number of students and faculty "
                "participating in each activity, with activities on the x-axis and "
                "participant type shown in different colors."
            ),
            "time": "2026-05-19 10:30:00",
            "results": {
                "chart_img": "/history/chart_result/4.png",
                "chart_json": "/history/chart_json/4.vega.json",
                "chart_backup_name": "4.png",
                "chart_json_backup_name": "4.vega.json",
                "sql": (
                    "SELECT a.activity_name, 'Student' AS participant_type,"
                    " COUNT(*) AS participant_count\n"
                    "FROM Participates_in p JOIN Activity a ON a.actid = p.actid\n"
                    "GROUP BY a.activity_name\n"
                    "UNION ALL\n"
                    "SELECT a.activity_name, 'Faculty', COUNT(*)\n"
                    "FROM Faculty_Participates_in fp"
                    " JOIN Activity a ON a.actid = fp.actid\n"
                    "GROUP BY a.activity_name;"
                ),
                "eval_result": (
                    "=== Evaluation Results ===\n"
                    "✅ Passed — Clear stacked bar chart with legend and "
                    "readable activity labels."
                ),
                "vis_code": STACKED_BAR_CODE,
                "is_database_code": False,
            },
            "uploaded_image_name": None,
            "original_image_name": None,
        },
        {
            "db_name": "activity_1.sqlite",
            "query": (
                "Scatter plot: average student age per activity vs overall average. "
                "Use a red-blue color scheme and add a descriptive title."
            ),
            "time": "2026-05-19 09:15:00",
            "results": {
                "chart_img": "/history/chart_result/3.png",
                "chart_json": "/history/chart_json/3.vega.json",
                "chart_backup_name": "3.png",
                "chart_json_backup_name": "3.vega.json",
                "eval_result": (
                    "=== Evaluation Results ===\n"
                    "✅ Passed — Reference-consistent scatter with red-blue encoding."
                ),
                "vis_code": SCATTER_CODE,
                "is_database_code": False,
            },
            "uploaded_image_name": "3.png",
            "original_image_name": "reference_scatter.png",
        },
        {
            "db_name": "chinook_1.sqlite",
            "query": (
                "Colorful pie chart of track counts per music genre from "
                "chinook_1.sqlite, sorted by size, using Altair."
            ),
            "time": "2026-05-19 08:45:00",
            "results": {
                "chart_img": "/history/chart_result/2.png",
                "chart_json": "/history/chart_json/2.vega.json",
                "chart_backup_name": "2.png",
                "chart_json_backup_name": "2.vega.json",
                "sql": (
                    "SELECT g.Name AS genre, COUNT(t.TrackId) AS tracks\n"
                    "FROM Track t JOIN Genre g ON g.GenreId = t.GenreId\n"
                    "GROUP BY g.Name ORDER BY tracks DESC;"
                ),
                "eval_result": (
                    "=== Evaluation Results ===\n"
                    "✅ Passed — Genre distribution pie chart with tooltips."
                ),
                "vis_code": PIE_CODE,
                "is_database_code": False,
            },
            "uploaded_image_name": None,
            "original_image_name": None,
        },
        {
            "db_name": "activity_1.sqlite",
            "query": (
                "Improve the age-delta chart: rotate x-axis labels, add y-axis grid lines, "
                "and use larger hollow points with the same color scheme."
            ),
            "time": "2026-05-19 08:00:00",
            "results": {
                "chart_img": "/history/chart_result/1.png",
                "chart_json": "/history/chart_json/1.vega.json",
                "chart_backup_name": "1.png",
                "chart_json_backup_name": "1.vega.json",
                "eval_result": (
                    "=== Evaluation Results ===\n"
                    "✅ Passed — Improved readability with rotated labels and grid."
                ),
                "vis_code": REFINED_SCATTER_CODE,
                "mod_code": SCATTER_CODE,
                "code": SCATTER_CODE,
                "is_database_code": True,
            },
            "uploaded_image_name": None,
            "original_image_name": None,
        },
    ]

    out = HISTORY / "history.json"
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(items)} items)")

    # Trim any stray chart artefacts left behind by previous test runs so the
    # shipped demo only contains the four canonical previews.
    keep_pngs = {f"{n}.png" for n in (1, 2, 3, 4)}
    keep_jsons = {f"{n}.vega.json" for n in (1, 2, 3, 4)}
    for p in CHART_RESULT.glob("*.png"):
        if p.name not in keep_pngs:
            p.unlink(missing_ok=True)
    for p in CHART_JSON.glob("*.vega.json"):
        if p.name not in keep_jsons:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
