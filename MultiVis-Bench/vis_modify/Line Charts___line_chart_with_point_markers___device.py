import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/device.sqlite')

query = """
SELECT Open_Year, COUNT(Shop_ID) AS Shop_Count
FROM shop
GROUP BY Open_Year
ORDER BY Open_Year
"""

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('Open_Year:O', title='Year Opened'),
    y=alt.Y('Shop_Count:Q', title='Number of Shops Opened'),
    tooltip=['Open_Year', 'Shop_Count']
).properties(
    title='Trend of Shop Openings Over Years'
)

chart