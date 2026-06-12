import altair as alt
import pandas as pd

text = """
It was the best of times, it was the worst of times, it was the age of wisdom,
it was the age of foolishness, it was the epoch of belief, it was the epoch of
incredulity, it was the season of Light, it was the season of Darkness, it was
the spring of hope, it was the winter of despair, we had everything before us,
we had nothing before us, we were all going direct to Heaven, we were all going
direct the other way - in short, the period was so far like the present period,
that some of its noisiest authorities insisted on its being received, for good
or for evil, in the superlative degree of comparison only.
"""

source = pd.DataFrame(
    {'letters': [c.lower() for c in text if c.isalpha()]}
)

chart = alt.Chart(source).transform_aggregate(
    count='count()',
    groupby=['letters']
).transform_window(
    rank='rank(count)',
    sort=[alt.SortField('count', order='descending')]
).transform_filter(
    alt.datum.rank <= 10
).mark_bar().encode(
    x='count:Q',
    y=alt.Y('letters:N', sort='-x')
)

chart