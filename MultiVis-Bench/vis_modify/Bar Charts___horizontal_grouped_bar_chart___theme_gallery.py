import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/theme_gallery.sqlite')

query = '''
SELECT 
    e.Theme AS Theme, 
    e.Year AS Year, 
    SUM(er.Attendance) AS Total_Attendance
FROM 
    exhibition AS e
JOIN 
    exhibition_record AS er ON e.Exhibition_ID = er.Exhibition_ID
GROUP BY 
    e.Theme, e.Year
ORDER BY 
    e.Theme, e.Year
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Total_Attendance:Q',
    y='Theme:N',
    color='Year:N',
    row='Theme:N'
).properties(
    width=600,
    height=100
)

chart