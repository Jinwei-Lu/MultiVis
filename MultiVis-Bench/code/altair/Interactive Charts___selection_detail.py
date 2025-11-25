import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)

n_objects = 20
n_times = 50

locations = pd.DataFrame({
    'id': range(n_objects),
    'x': np.random.uniform(-2, 2, n_objects),
    'y': np.random.uniform(-2, 2, n_objects)
})

timeseries = pd.DataFrame(np.random.randn(n_times, n_objects).cumsum(0),
                          columns=locations['id'],
                          index=pd.RangeIndex(0, n_times, name='time'))

timeseries = timeseries * 1.5

timeseries = timeseries.reset_index().melt('time')
timeseries['id'] = timeseries['id'].astype(int)
data = pd.merge(timeseries, locations, on='id')

selector = alt.selection_point(fields=['id'])
color = alt.condition(selector,
                      alt.Color("id:O"),
                      alt.value("lightgray"))

base = alt.Chart(data).add_params(selector)

points = base.mark_point().encode(
    x='mean(x)',
    y='mean(y)',
    color=color,
)

line = base.mark_line().encode(
    x='time',
    y='value',
    color=alt.Color('id:O')
).transform_filter(
    selector
)

points | line