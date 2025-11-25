import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/company_employee.sqlite')

query = '''
SELECT 
    p.Graduation_College AS College,
    c.Industry AS Industry,
    COUNT(*) AS Employee_Count
FROM 
    employment AS e
JOIN 
    people AS p ON e.People_ID = p.People_ID
JOIN 
    company AS c ON e.Company_ID = c.Company_ID
GROUP BY 
    p.Graduation_College, c.Industry
ORDER BY 
    p.Graduation_College, c.Industry;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    alt.Theta("Employee_Count:Q").stack(True),
    alt.Radius("Employee_Count").scale(type="sqrt", zero=True, rangeMin=20),
    color="Industry:N",
    tooltip=["College:N", "Industry:N", "Employee_Count:Q"]
)

c1 = base.mark_arc(innerRadius=20, stroke="#fff")
c2 = base.mark_text(radiusOffset=10).encode(text="Employee_Count:Q")
chart = c1 + c2

chart.properties(title="Employee Distribution by Graduation College and Industry")