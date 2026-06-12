import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n_points = 100
categories = ["A", "B", "C"]

data = {}
for i, cat in enumerate(categories):
    data[cat] = np.cumsum(np.random.randn(n_points)) + (i * 5)

source = pd.DataFrame(data)
source["x"] = np.arange(n_points)
source = source.melt("x", var_name="category", value_name="y")

nearest = alt.selection_point(nearest=True, on="mouseover", fields=["x"], empty=False)

line = alt.Chart(source).mark_line().encode(
    x="x:Q",
    y="y:Q",
    color="category:N"
)

selectors = alt.Chart(source).mark_point().encode(
    x="x:Q",
    opacity=alt.value(0),
).add_params(nearest)

when_near = alt.condition(nearest, alt.value(1), alt.value(0))

points = line.mark_point().encode(
    opacity=when_near
)

text = line.mark_text().encode(
    text=alt.condition(nearest, alt.Text("y:Q"), alt.value(" "))
)

rules = alt.Chart(source).mark_rule().encode(
    x="x:Q",
).transform_filter(nearest)

alt.layer(line, selectors, points, rules, text)