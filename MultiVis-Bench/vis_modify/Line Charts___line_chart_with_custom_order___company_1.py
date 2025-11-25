import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/company_1.sqlite')

query = '''
SELECT 
    p.Pname AS Project_Name,
    p.Pnumber AS Project_Number,
    SUM(w.Hours) AS Total_Hours
FROM 
    works_on AS w
JOIN 
    project AS p ON w.Pno = p.Pnumber
GROUP BY 
    p.Pnumber, p.Pname
ORDER BY 
    p.Pnumber
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Project_Number:O").title("Project Number"),
    y=alt.Y("Total_Hours:Q").title("Total Hours Worked"),
    order="Project_Number",
    tooltip=["Project_Name", "Total_Hours", "Project_Number"]
)

chart