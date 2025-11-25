import altair as alt
import pandas as pd
import numpy as np

rand = np.random.RandomState(42)

df = pd.DataFrame({
    'xval': range(100),
    'yval': rand.randn(100).cumsum()
})

slider = alt.binding_range(min=0, max=100, step=1)
cutoff = alt.param(bind=slider, value=50)
predicate = alt.datum.xval < cutoff

chart = alt.Chart(df).mark_point().encode(
    x='xval',
    y='yval',
    color=alt.condition(predicate, alt.value("red"), alt.value("blue")),
).add_params(
    cutoff
)

chart