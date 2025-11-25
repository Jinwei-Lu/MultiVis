import pandas as pd
import altair as alt

data = {
    'x': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
    'y': [8.5, 7.2, 6.8, 7.5, 8.1, 8.3, 8.6, 8.8, 9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.75, 9.8, 9.85, 9.9]
}
source = pd.DataFrame(data)

degree_list = [1, 3, 5]

base = alt.Chart(source).mark_circle().encode(
    alt.X("x"),
    alt.Y("y")
)

polynomial_fit = [
    base.transform_regression(
        "x", "y", method="poly", order=order, as_=["x", str(order)]
    )
    .mark_line()
    .transform_fold([str(order)], as_=["degree", "y"])
    .encode(alt.Color("degree:N"))
    for order in degree_list
]

chart = alt.layer(base, *polynomial_fit)
chart