import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/network_1.sqlite')

query = '''
SELECT 
    T1.ID AS student_id, 
    T1.name AS student_name, 
    COUNT(T2.friend_id) AS friend_count
FROM 
    Highschooler AS T1
LEFT JOIN 
    Friend AS T2 ON T1.ID = T2.student_id
GROUP BY 
    T1.ID, T1.name
'''

df = pd.read_sql_query(query, conn)
conn.close()

bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('student_name:N', title='Student Name'),
    y=alt.Y('friend_count:Q', title='Number of Friends')
)

rule = alt.Chart(df).mark_rule(color='red').encode(
    y='mean(friend_count):Q'
)

chart = (bar + rule).properties(
    width=600,
    title='Number of Friends per Student with Average Line'
)

chart