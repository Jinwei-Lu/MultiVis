import math
import altair as alt
import pandas as pd

source = pd.DataFrame({
    "hour": range(24),
    "observations": [2, 2, 2, 2, 2, 3, 4, 4, 8, 8, 9, 7, 5, 6, 8, 8, 7, 7, 4, 3, 3, 2, 2, 2]
})

polar_bars = alt.Chart(source).mark_arc().encode(
    theta=alt.Theta("hour:O"),
    radius=alt.Radius('observations').scale(type='linear'),
    radius2=alt.datum(1)
)

axis_rings = alt.Chart(pd.DataFrame({"ring": range(2, 11, 2)})).mark_arc().encode(
    theta=alt.value(2 * math.pi),
    radius=alt.Radius('ring').stack(False)
)

axis_lines = alt.Chart(pd.DataFrame({
    "radius": 10,
    "theta": math.pi / 2,
    'hour': ['00:00', '06:00', '12:00', '18:00']
})).mark_arc().encode(
    theta=alt.Theta('theta').stack(True),
    radius=alt.Radius('radius'),
    radius2=alt.datum(1)
)

axis_lines_labels = axis_lines.mark_text().encode(text="hour")

chart = alt.layer(
    axis_rings,
    polar_bars,
    axis_lines,
    axis_lines_labels
)

chart