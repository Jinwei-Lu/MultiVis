import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/e_learning.sqlite')

query = '''
SELECT 
    strftime('%H', date_of_registration) AS hour_of_registration,
    COUNT(*) AS registration_count
FROM Students
GROUP BY hour_of_registration
ORDER BY hour_of_registration
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval(encodings=['x'])

base = alt.Chart(df).mark_bar().encode(
    y='registration_count:Q'
).properties(
    width=600,
    height=100
)

chart = alt.vconcat(
    base.encode(
        alt.X('hour_of_registration:Q')
          .bin(maxbins=24, extent=brush)
          .scale(domain=brush),
        y='registration_count:Q'
    ),
    base.encode(
        alt.X('hour_of_registration:Q').bin(maxbins=24),
        y='registration_count:Q'
    ).add_params(brush)
)

chart