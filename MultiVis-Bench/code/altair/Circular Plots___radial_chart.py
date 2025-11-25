import pandas as pd
import altair as alt

source = pd.DataFrame({
    "category": ["A", "B", "C", "D", "E", "F"],
    "values": [25, 18, 32, 15, 40, 28]
})

base = alt.Chart(source).encode(
    alt.Theta("values:Q").stack(True),
    alt.Radius("values:Q").scale(type="sqrt", zero=True, rangeMin=20),
    alt.Color("category:N")
)

c1 = base.mark_arc(innerRadius=20)

c2 = base.mark_text(radiusOffset=10).encode(
    text="values:Q"
)

c1 + c2