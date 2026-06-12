import pandas as pd
import numpy as np
import altair as alt

rng = np.random.default_rng(905)
num_rows = 10
num_cols = 4
column_names = ['a', 'b', 'c', 'd']
data = rng.random((num_rows, num_cols))

start_date = '2022-02-13'
dates = pd.date_range(start=start_date, periods=num_rows).strftime('%Y-%m-%d')

ex_ts = pd.DataFrame(data, columns=column_names)
ex_ts['date'] = dates

select_x = alt.selection_point(fields=['level_0'], name='select_x', value='b')
select_y = alt.selection_point(fields=['level_1'], name='select_y', value='d')

heatmap_data = ex_ts.drop(columns='date').corr().stack().reset_index().rename(columns={0: 'correlation'})

heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    alt.X('level_0'),
    alt.Y('level_1'),
    alt.Color('correlation').scale(domain=[-1, 1]),
    opacity=alt.when(select_x, select_y).then(alt.value(1)).otherwise(alt.value(0.4)),
).add_params(
    select_x, select_y
)

base = alt.Chart(
    ex_ts.melt(
        id_vars='date',
        var_name='category',
        value_name='value',
    )
)
lines = base.transform_filter(
    'indexof(datum.category, select_x.level_0) !== -1 | indexof(datum.category, select_y.level_1) !== -1'
).mark_line().encode(
    alt.X('date:T'),
    alt.Y('value'),
    alt.Color('category')
)

lines_diff = base.transform_pivot(
    'category', 'value', groupby=['date']
).transform_calculate(
    difference = f'datum[{select_x.name}.level_0] - datum[{select_y.name}.level_1]'
).mark_line().encode(
    alt.X('date:T'),
    alt.Y('difference:Q')
)

(lines & lines_diff) | heatmap