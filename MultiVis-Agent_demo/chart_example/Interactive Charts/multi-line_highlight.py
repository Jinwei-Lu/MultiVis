import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)

date_range = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

symbols = ['AAPL', 'GOOG', 'MSFT']
data = []
for symbol in symbols:
    price = np.random.randint(50, 200)
    prices = [price]
    for _ in range(1, len(date_range)):
        price_change = np.random.normal(loc=0.001, scale=0.02) * price
        price += price_change
        prices.append(price)
    df = pd.DataFrame({
        'date': date_range,
        'price': prices,
        'symbol': symbol
    })
    data.append(df)

source = pd.concat(data)

highlight = alt.selection_point(on='mouseover', fields=['symbol'], nearest=True)

base = alt.Chart(source).encode(
    x='date:T',
    y='price:Q',
    color='symbol:N'
)

points = base.mark_circle().encode(
    opacity=alt.value(0)
).add_params(
    highlight
)

lines = base.mark_line().encode(
    size=alt.condition(~highlight, alt.value(1), alt.value(3))
)

points + lines