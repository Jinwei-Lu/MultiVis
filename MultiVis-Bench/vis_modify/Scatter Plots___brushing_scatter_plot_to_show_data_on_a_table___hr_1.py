import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/hr_1.sqlite')

query = '''
SELECT 
    e.FIRST_NAME,
    e.LAST_NAME,
    e.SALARY,
    e.COMMISSION_PCT,
    j.JOB_TITLE,
    d.DEPARTMENT_NAME
FROM 
    employees AS e
JOIN 
    jobs AS j ON e.JOB_ID = j.JOB_ID
JOIN 
    departments AS d ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval()

points = alt.Chart(df).mark_point().encode(
    x=alt.X('SALARY:Q', title='Salary'),
    y=alt.Y('COMMISSION_PCT:Q', title='Commission Percentage'),
    color=alt.condition(brush, alt.value("steelblue"), alt.value("grey"))
).add_params(brush)

ranked_text = alt.Chart(df).mark_text(align='right').encode(
    y=alt.Y('row_number:O').axis(None)
).transform_filter(
    brush
).transform_window(
    row_number='row_number()'
).transform_filter(
    alt.datum.row_number < 15
)

first_name = ranked_text.encode(text='FIRST_NAME:N').properties(
    title=alt.Title(text='First Name', align='right')
)
last_name = ranked_text.encode(text='LAST_NAME:N').properties(
    title=alt.Title(text='Last Name', align='right')
)
job_title = ranked_text.encode(text='JOB_TITLE:N').properties(
    title=alt.Title(text='Job Title', align='right')
)
department_name = ranked_text.encode(text='DEPARTMENT_NAME:N').properties(
    title=alt.Title(text='Department', align='right')
)
text = alt.hconcat(first_name, last_name, job_title, department_name)

chart = alt.hconcat(
    points,
    text
).resolve_legend(
    color="independent"
).configure_view(
    stroke=None
)

chart.show()