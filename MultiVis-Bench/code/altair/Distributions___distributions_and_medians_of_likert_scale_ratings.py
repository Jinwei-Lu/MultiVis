import altair as alt
import pandas as pd

medians = pd.DataFrame(
    [
        {"name": "Identify Errors:", "median": 2.0, "lo": "Easy", "hi": "Hard"},
        {"name": "Fix Errors:", "median": 2.5, "lo": "Easy", "hi": "Hard"},
        {"name": "Easier to Fix:", "median": 2.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Faster to Fix:", "median": 3.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Phone:", "median": 1.8, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Tablet:", "median": 3.2, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Device Preference:", "median": 4.0, "lo": "Phone", "hi": "Tablet"},
    ]
)

values_data = {
    "Identify Errors:": [2, 2, 2, 3, 2, 1, 2, 3, 2, 2, 2, 1, 2, 3, 4, 1, 3],
    "Fix Errors:": [2, 3, 2, 3, 2, 3, 3, 1, 3, 2, 2, 3, 2, 3, 5, 3, 2],
    "Easier to Fix:": [3, 4, 2, 2, 4, 3, 4, 2, 2, 1, 1, 2, 1, 2, 1, 2, 2],
    "Faster to Fix:": [4, 5, 1, 2, 4, 4, 5, 4, 4, 1, 1, 3, 1, 2, 1, 2, 2],
    "Easier on Phone:": [2, 5, 2, 4, 4, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "Easier on Tablet:": [5, 5, 1, 1, 5, 4, 2, 5, 4, 1, 1, 3, 1, 1, 1, 4, 3],
    "Device Preference:": [5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 4, 3, 5, 1, 5, 5, 2],
}

values = []
for name, vals in values_data.items():
    for v in vals:
        values.append({"name": name, "value": v})
values = pd.DataFrame(values)

y_axis = alt.Y("name:N")

base = alt.Chart(medians).encode(y_axis)

bubbles = (
    alt.Chart(values)
    .mark_circle()
    .encode(
        alt.X("value:Q").scale(domain=[0, 6]),
        y_axis,
        size=alt.Size("count():Q"),
    )
)

ticks = base.mark_tick().encode(
    alt.X("median:Q").scale(domain=[0, 6])
)

texts_lo = base.mark_text(align="right", dx=-5).encode(
    text="lo:N"
)

texts_hi = base.mark_text(align="left", dx=5).encode(
    alt.X("max(value):Q", aggregate="max"),
    text="hi:N",
)

chart = bubbles + ticks + texts_lo + texts_hi

chart