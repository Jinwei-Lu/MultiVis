import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
x_values = range(100)
data = {
    'x': x_values,
    'A': [i + np.random.uniform(-2, 2) for i in x_values],
    'B': [np.sin(i/5) * 20 + np.random.uniform(-3, 3) for i in x_values],
    'C': [i**0.5 * 5 + np.random.uniform(-1, 1) for i in x_values]
}
source = pd.DataFrame(data)
source = source.melt("x", var_name="category", value_name="y")

nearest = alt.selection_point(nearest=True, on="pointerover", fields=["x"], empty=False)

line = alt.Chart(source).mark_line(interpolate="basis").encode(
    x="x:Q",
    y="y:Q",
    color="category:N"
)

points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

rules = alt.Chart(source).transform_pivot(
    "category",
    value="y",
    groupby=["x"]
).mark_rule().encode(
    x="x:Q",
    opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
    tooltip=[alt.Tooltip(c, type="quantitative") for c in ["A", "B", "C"]],
).add_params(nearest)

alt.layer(line, points, rules)