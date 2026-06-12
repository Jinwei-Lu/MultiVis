import altair as alt
import numpy as np
import calendar
import pandas as pd

months = list(calendar.month_abbr)[1:]
temp_min = np.random.randint(-10, 25, size=12)
temp_max = temp_min + np.random.randint(5, 20, size=12)

data = pd.DataFrame({'month': months, 'temp_min': temp_min, 'temp_max': temp_max})
data['month_date'] = pd.to_datetime(data['month'], format='%b').dt.strftime('1900-%m-%d')

bar = alt.Chart(data).mark_bar().encode(
    x=alt.X('temp_min:Q', scale=alt.Scale(domain=[-15, 45])),
    x2='temp_max:Q',
    y=alt.Y('month_date:T', timeUnit='month')
)

text_min = alt.Chart(data).mark_text().encode(
    x=alt.X('temp_min:Q'),
    y=alt.Y('month_date:T', timeUnit='month'),
    text=alt.Text('temp_min:Q', format='.0f')
)

text_max = alt.Chart(data).mark_text().encode(
    x=alt.X('temp_max:Q'),
    y=alt.Y('month_date:T', timeUnit='month'),
    text=alt.Text('temp_max:Q', format='.0f')
)

chart = bar + text_min + text_max
chart