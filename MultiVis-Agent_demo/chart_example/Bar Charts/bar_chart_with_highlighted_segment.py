import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
years = np.arange(1565, 1825, 5)
wheat = np.random.randint(20, 70, size=len(years))
for i in range(len(years) - 10, len(years)):
    wheat[i] = wheat[i] + (i - (len(years) - 10)) * 5

source = pd.DataFrame({'year': years, 'wheat': wheat})
threshold_value = 90

base = alt.Chart(source).encode(
    x=alt.X('year:O'),
)

bars = base.mark_bar().encode(
    y=alt.Y('wheat:Q')
)

source_above = source[source['wheat'] > threshold_value].copy()
source_above['wheat_above'] = source_above['wheat'] - threshold_value
source_above['threshold'] = threshold_value

bars_above = alt.Chart(source_above).mark_bar().encode(
    x=alt.X('year:O'),
    y='threshold:Q',
    y2='wheat:Q'
)

rule = alt.Chart(pd.DataFrame({'threshold': [threshold_value]})).mark_rule().encode(
    y='threshold:Q'
)

chart = bars + bars_above + rule
chart.show()