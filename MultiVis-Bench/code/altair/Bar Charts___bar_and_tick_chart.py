import altair as alt
import pandas as pd

project = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
score = [25, 57, 23, 19, 8, 47, 8]
goal = [25, 47, 30, 27, 38, 19, 4]

source = pd.DataFrame({
    'project': project,
    'score': score,
    'goal': goal
})

bar = alt.Chart(source).mark_bar().encode(
    x='project:N',
    y='score:Q'
)

tick = alt.Chart(source).mark_tick().encode(
    x='project:N',
    y='goal:Q'
)

combined_chart = bar + tick

combined_chart