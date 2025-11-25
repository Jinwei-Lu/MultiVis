import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/employee_hire_evaluation.sqlite')

query = '''
SELECT e.City, ev.Year_awarded, SUM(ev.Bonus) AS Total_Bonus
FROM employee AS e
JOIN evaluation AS ev ON e.Employee_ID = ev.Employee_ID
WHERE e.City = 'Bristol'
GROUP BY ev.Year_awarded
ORDER BY ev.Year_awarded
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_area(
    line={'color': 'darkblue'},
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='white', offset=0),
               alt.GradientStop(color='darkblue', offset=1)],
        x1=1,
        x2=1,
        y1=1,
        y2=0
    )
).encode(
    alt.X('Year_awarded:T', title='Year'),
    alt.Y('Total_Bonus:Q', title='Total Bonus Awarded')
).properties(
    title='Total Bonuses Awarded Over Years for Employees from Bristol'
)

chart