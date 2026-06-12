import altair as alt
import pandas as pd
import numpy as np
import datetime as dt

np.random.seed(0)
start_date = dt.date(2007, 1, 1)
end_date = dt.date(2010, 1, 1)
dates = pd.date_range(start_date, end_date, freq='D')
prices = 1000 + np.cumsum(np.random.randn(len(dates)) * 10)

source = pd.DataFrame({'date': dates, 'price': prices})

date_range = (dt.date(2007, 6, 30), dt.date(2009, 6, 30))

brush = alt.selection_interval(encodings=['x'],
                               value={'x': [pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])]},
                               resolve='global')

base = alt.Chart(source).mark_area().encode(
    x=alt.X('date:T'),
    y=alt.Y('price:Q')
)

upper = base.encode(
    alt.X('date:T', scale=alt.Scale(domain=brush))
)

lower = base.add_params(brush)

chart = upper & lower

chart