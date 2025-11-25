import altair as alt
import pandas as pd

source = pd.DataFrame({
    'Activity': ['Sleeping', 'Eating', 'TV', 'Work', 'Exercise'],
    'Time': [8, 2, 4, 8, 2]
})

alt.Chart(source).transform_joinaggregate(
    TotalTime='sum(Time)',
).transform_calculate(
    PercentOfTotal="datum.Time / datum.TotalTime"
).mark_bar().encode(
    alt.X('PercentOfTotal:Q'),
    y='Activity:N'
)