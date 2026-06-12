import pandas as pd
import altair as alt

data = {
    'category': [1, 2, 3, 4, 5, 6],
    'value': [4, 6, 10, 3, 7, 8]
}
source = pd.DataFrame(data)

chart = alt.Chart(source).mark_arc().encode(
    theta=alt.Theta(field="value", type="quantitative"),
    color=alt.Color(field="category", type="nominal")
)

chart.show()