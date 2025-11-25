import altair as alt
import pandas as pd

new_data = pd.DataFrame({
    'region': ['North', 'North', 'South', 'South', 'East', 'East', 'West', 'West'],
    'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
    'sales_amount': [100, 150, 80, 120, 200, 90, 130, 110]
})

base = alt.Chart(new_data).encode(
    x=alt.X('sum(sales_amount):Q').stack('zero'),
    y=alt.Y('region:O').sort('-x')
)

bars = base.mark_bar().encode()

text = base.mark_text()

chart = bars + text

chart