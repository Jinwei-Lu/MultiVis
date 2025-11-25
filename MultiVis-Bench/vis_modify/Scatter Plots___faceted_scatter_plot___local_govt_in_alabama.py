import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/local_govt_in_alabama.sqlite')

query = '''
SELECT 
    S.Service_Type_Code,
    COUNT(DISTINCT P.Participant_ID) AS Participant_Count,
    AVG(CASE WHEN E.Event_Details = 'Success' THEN 1 ELSE 0 END) * 100 AS Success_Rate
FROM 
    Events AS E
JOIN 
    Services AS S ON E.Service_ID = S.Service_ID
JOIN 
    Participants_in_Events AS PE ON E.Event_ID = PE.Event_ID
JOIN 
    Participants AS P ON PE.Participant_ID = P.Participant_ID
GROUP BY 
    S.Service_Type_Code
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_point().encode(
    x=alt.X("Participant_Count:Q", title="Number of Participants"),
    y=alt.Y("Success_Rate:Q", title="Success Rate (%)"),
    row=alt.Row("Service_Type_Code:N", title="Service Type")
).properties(
    width=200,
    height=200
)

chart.show()