import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/baseball_1.sqlite')

query = '''
SELECT 
    year,
    league_id,
    SUM(hr) AS total_hr
FROM 
    batting
WHERE 
    league_id IN ('NL', 'AL') AND hr IS NOT NULL
GROUP BY 
    year, league_id
ORDER BY 
    year ASC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

bars = alt.Chart(df).mark_bar().encode(
    x=alt.X('sum(total_hr):Q').stack('zero').title('Total Home Runs'),
    y=alt.Y('year:N').title('Year'),
    color=alt.Color('league_id:N').title('League')
)

text = alt.Chart(df).mark_text(dx=-15, dy=3, color='white').encode(
    x=alt.X('sum(total_hr):Q').stack('zero'),
    y=alt.Y('year:N'),
    detail='league_id:N',
    text=alt.Text('sum(total_hr):Q', format='.0f')
)

chart = bars + text
chart.properties(title="Total Home Runs by League Over the Years")