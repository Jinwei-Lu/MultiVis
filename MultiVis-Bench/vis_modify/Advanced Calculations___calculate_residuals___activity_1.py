import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/activity_1.sqlite')

query = '''
SELECT 
    A.activity_name,
    AVG(S.Age) AS Avg_Age
FROM 
    Activity AS A
JOIN 
    Participates_in AS P ON A.actid = P.actid
JOIN 
    Student AS S ON P.stuid = S.StuID
GROUP BY 
    A.actid, A.activity_name
'''

df = pd.read_sql_query(query, conn)

conn.close()

overall_avg_age = df['Avg_Age'].mean()

chart = (
    alt.Chart(df)
    .mark_point()
    .transform_calculate(
        Age_Delta="datum.Avg_Age - " + str(overall_avg_age)
    )
    .encode(
        x=alt.X("activity_name:N").title("Activity Name"),
        y=alt.Y("Age_Delta:Q").title("Age Delta (Years)"),
        color=alt.Color("Age_Delta:Q")
        .title("Age Delta")
        .scale(domainMid=0, scheme="redblue"),
    )
    .properties(title="Difference in Average Age by Activity")
)

chart