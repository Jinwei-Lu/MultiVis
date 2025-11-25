import altair as alt
import pandas as pd
import numpy as np

medians = pd.DataFrame(
    [
        {"name": "Identify Errors:", "median": 2.0, "lo": "Easy", "hi": "Hard"},
        {"name": "Fix Errors:", "median": 2.1, "lo": "Easy", "hi": "Hard"},
        {"name": "Easier to Fix:", "median": 2.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Faster to Fix:", "median": 2.6, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Phone:", "median": 1.6, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Tablet:", "median": 3.1, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Device Preference:", "median": 4.6, "lo": "Phone", "hi": "Tablet"},
    ]
)

values_data = []
for name in medians['name']:
    for value in range(1, 6):
        count = np.random.randint(0, 10)
        values_data.append({'name': name, 'value': value, 'count': count})
values = pd.DataFrame(values_data)

y_axis = alt.Y("name:N")

base = alt.Chart(medians).encode(y_axis)

bubbles = alt.Chart(values).mark_circle().encode(
    x=alt.X("value:Q"),
    y=y_axis,
    size=alt.Size("count:Q"),
)

ticks = base.mark_tick().encode(
    x=alt.X("median:Q"),
)

texts_lo = base.mark_text().encode(
    text="lo:N"
)

texts_hi = base.mark_text().encode(
    text="hi:N"
)

chart = bubbles + ticks + texts_lo + texts_hi
chart.show()