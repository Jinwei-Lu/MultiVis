import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.to_datetime(['2023-01-01'] + [pd.Timestamp('2023-01-01') + pd.Timedelta(days=i) for i in range(1, 365)])
temp_max = np.random.uniform(5, 25, size=365)

source = pd.DataFrame({'date': dates, 'temp_max': temp_max})
source['month'] = source['date'].dt.month_name()
source['day'] = source['date'].dt.day

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

alt.Chart(source).mark_rect().encode(
    alt.X("date:T", timeUnit="date"),
    alt.Y("date:T", timeUnit="month", sort=month_order),
    alt.Color("temp_max:Q"),
    tooltip=[
        alt.Tooltip("date:T", timeUnit="monthdate"),
        alt.Tooltip("temp_max:Q", format=".1f"),
    ],
)