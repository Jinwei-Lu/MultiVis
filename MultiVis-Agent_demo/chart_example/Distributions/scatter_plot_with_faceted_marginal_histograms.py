import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 150
species = np.repeat(['setosa', 'versicolor', 'virginica'], n_samples / 3)
sepal_length = np.concatenate([
    np.random.normal(5.0, 0.35, int(n_samples / 3)),
    np.random.normal(5.9, 0.5, int(n_samples / 3)),
    np.random.normal(6.5, 0.6, int(n_samples / 3)),
])
sepal_width = np.concatenate([
    np.random.normal(3.4, 0.4, int(n_samples / 3)),
    np.random.normal(2.7, 0.3, int(n_samples / 3)),
    np.random.normal(3.0, 0.4, int(n_samples / 3)),
])

df = pd.DataFrame({'sepalLength': sepal_length, 'sepalWidth': sepal_width, 'species': species})

xscale = alt.Scale(domain=(4.0, 8.0))
yscale = alt.Scale(domain=(1.9, 4.55))

base = alt.Chart(df)

points = base.mark_circle().encode(
    alt.X("sepalLength:Q").scale(xscale),
    alt.Y("sepalWidth:Q").scale(yscale),
    alt.Color("species:N")
)

top_hist = base.mark_bar().encode(
    alt.X("sepalLength:Q").bin(maxbins=20, extent=xscale.domain),
    alt.Y('count()', stack=None),
    alt.Color('species:N')
)

right_hist = base.mark_bar().encode(
    alt.Y("sepalWidth:Q").bin(maxbins=20, extent=yscale.domain),
    alt.X('count()', stack=None),
    alt.Color('species:N')
)

top_hist & (points | right_hist)