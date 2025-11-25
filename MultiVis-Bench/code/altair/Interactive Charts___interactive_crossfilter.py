import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n_flights = 2000

start_date = pd.to_datetime('2024-01-01')
end_date = pd.to_datetime('2024-01-31')
dates = pd.to_datetime(np.random.uniform(start_date.value, end_date.value, n_flights))
distances = np.random.randint(100, 2000, n_flights)
delays = np.random.randint(-30, 120, n_flights)

data = pd.DataFrame({
    'date': dates,
    'distance': distances,
    'delay': delays
})

data['time'] = data['date'].dt.hour

source = alt.Data(values=data.to_dict(orient='records'))

brush = alt.selection_interval(encodings=['x'])

base = alt.Chart().mark_bar().encode(
    x=alt.X(alt.repeat('column')).bin(maxbins=20),
    y='count()'
)

background = base.encode().add_params(brush)
highlight = base.transform_filter(brush)

alt.layer(
    background,
    highlight,
    data=source
).repeat(column=["distance", "delay", "time"])