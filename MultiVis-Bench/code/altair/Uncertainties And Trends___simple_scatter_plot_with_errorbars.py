import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
x = [1, 2, 3, 4, 5]
y = np.random.normal(10, 0.5, size=len(x))
yerr = 0.2

source = pd.DataFrame({'x': x, 'y': y, 'yerr': yerr})
source['ymin'] = source['y'] - source['yerr']
source['ymax'] = source['y'] + source['yerr']

base = alt.Chart(source)

points = base.mark_point().encode(
    x='x',
    y='y'
)

errorbars = base.mark_errorbar().encode(
    x='x',
    y='ymin',
    y2='ymax'
)

chart = points + errorbars

chart