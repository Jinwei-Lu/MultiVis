import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/soccer_2.sqlite')
query = '''
SELECT 
    T.cName AS College,
    T.pPos AS Position,
    T.decision AS Decision,
    COUNT(T.pID) AS PlayerCount
FROM Tryout AS T
GROUP BY T.cName, T.pPos, T.decision
'''
df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x="College:N",
    y="PlayerCount:Q",
    xOffset="Position:N",
    color="Decision:N"
)

chart.show()