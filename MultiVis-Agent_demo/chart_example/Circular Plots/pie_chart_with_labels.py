import pandas as pd
import altair as alt

categories = ["a", "b", "c", "d", "e", "f"]
values = [4, 6, 10, 3, 7, 8]

source = pd.DataFrame({"category": categories, "value": values})

base = alt.Chart(source).encode(
    alt.Theta("value:Q", stack=True),
    alt.Color("category:N", legend=None)
)

pie = base.mark_arc()

text = base.mark_text().encode(
    text="category:N"
)

final_chart = pie + text

final_chart