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
    exhibition_record AS er
ON 
    e.Exhibition_ID = er.Exhibition_ID
GROUP BY 
    e.Theme, e.Year
ORDER BY 
    e.Theme, e.Year
'''
df = pd.read_sql_query(query, conn)
conn.close()

selection = alt.selection_point(fields=['Year'], bind='legend')

chart = alt.Chart(df).mark_bar().transform_calculate(
    year_order=f"if({selection.name}.Year && indexof({selection.name}.Year, datum.Year) !== -1, 0, 1)"
).encode(
    x=alt.X('sum(Total_Attendance):Q', title='Total Attendance'),
    y=alt.Y('Theme:N', title='Exhibition Theme'),
    color=alt.Color('Year:N', title='Year'),
    order=alt.Order('year_order:N'),
    opacity=alt.condition(selection, alt.value(0.9), alt.value(0.2))
).add_params(
    selection
)

chart.show()