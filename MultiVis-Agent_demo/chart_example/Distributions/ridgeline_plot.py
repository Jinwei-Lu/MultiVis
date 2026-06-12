import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n_days = 365 * 4
dates = pd.date_range('2012-01-01', periods=n_days, freq='D')
temp_max = np.random.randint(5, 35, size=n_days)

source_df = pd.DataFrame({
    'date': dates,
    'temp_max': temp_max,
})

source = source_df

step = 20
overlap = 1

alt.Chart(source, height=step).transform_timeunit(
    Month='month(date)'
).transform_joinaggregate(
    mean_temp='mean(temp_max)', groupby=['Month']
).transform_bin(
    ['bin_max', 'bin_min'], 'temp_max'
).transform_aggregate(
    value='count()', groupby=['Month', 'mean_temp', 'bin_min', 'bin_max']
).transform_impute(
    impute='value', groupby=['Month', 'mean_temp'], key='bin_min', value=0
).mark_area(
    interpolate='monotone'
).encode(
    alt.X('bin_min:Q', bin='binned'),
    alt.Y('value:Q', scale=alt.Scale(range=[step, -step * overlap])),
    alt.Fill('mean_temp:Q')
).facet(
    row=alt.Row('Month:T')
)