import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/activity_1.sqlite')

query = '''
SELECT 
    A.activity_name,
    COUNT(DISTINCT P.stuid) AS student_count,
    COUNT(DISTINCT F.FacID) AS faculty_count
FROM 
    Activity AS A
LEFT JOIN 
    Participates_in AS P ON A.actid = P.actid
LEFT JOIN 
    Faculty_Participates_in AS F ON A.actid = F.actid
GROUP BY 
    A.activity_name
'''

df = pd.read_sql_query(query, conn)
conn.close()

df_melted = df.melt(
    id_vars=['activity_name'], 
    value_vars=['student_count', 'faculty_count'], 
    var_name='participant_type', 
    value_name='count'
)

chart = alt.Chart(df_melted).mark_bar().encode(
    x='activity_name:N',
    y='sum(count):Q',
    color='participant_type:N'
)

chart.show()