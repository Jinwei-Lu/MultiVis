import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/film_rank.sqlite')

query = '''
SELECT 
    m.Country AS Country,
    SUM(f.Gross_in_dollar) AS Total_Gross
FROM 
    film_market_estimation AS fme
JOIN 
    film AS f ON fme.Film_ID = f.Film_ID
JOIN 
    market AS m ON fme.Market_ID = m.Market_ID
GROUP BY 
    m.Country
ORDER BY 
    Total_Gross DESC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).mark_area(
    clip=True,
    interpolate='monotone',
    opacity=0.6
).encode(
    alt.X('Country:N').title('Country'),
    alt.Y('Total_Gross:Q').scale(domain=[0, df['Total_Gross'].max() / 2]).title('Gross Revenue (Top Half)'),
).properties(
    width=500,
    height=75
)

top_half = base

bottom_half = base.encode(
    alt.Y('ny:Q').scale(domain=[0, df['Total_Gross'].max() / 2]).title('Gross Revenue (Bottom Half)')
).transform_calculate(
    "ny", alt.datum.Total_Gross - df['Total_Gross'].max() / 2
)

top_half + bottom_half