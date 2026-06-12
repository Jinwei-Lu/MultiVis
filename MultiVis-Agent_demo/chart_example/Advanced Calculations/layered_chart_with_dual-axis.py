import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
date_rng = pd.date_range(start='2012-01-01', end='2015-12-31', freq='M')
data = pd.DataFrame(date_rng, columns=['date'])
data['temp_max'] = 20 + 10 * np.sin(2 * np.pi * data.index / len(date_rng)) + np.random.randn(len(date_rng)) * 2
data['temp_min'] = 5 + 5 * np.sin(2 * np.pi * data.index / len(date_rng)) + np.random.randn(len(date_rng))
data['precipitation'] = 5 + np.random.rand(len(date_rng)) * 10
data['month'] = data['date'].dt.strftime('%b')

base = alt.Chart(data).encode(
    alt.X('month:N').scale(domain=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
)

area = base.mark_area(opacity=0.3).encode(
    alt.Y('mean(temp_max):Q'),
    alt.Y2('mean(temp_min):Q')
)

line = base.mark_line().encode(
    alt.Y('mean(precipitation):Q')
)

chart = alt.layer(area, line).resolve_scale(
    y='independent'
)

chart