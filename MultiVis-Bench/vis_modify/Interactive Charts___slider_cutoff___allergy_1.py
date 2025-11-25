import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/allergy_1.sqlite')

query = '''
SELECT S.Age, COUNT(*) AS NumStudents
FROM Student AS S
JOIN Has_Allergy AS HA ON S.StuID = HA.StuID
JOIN Allergy_Type AS AT ON HA.Allergy = AT.Allergy
WHERE AT.AllergyType = 'food'
GROUP BY S.Age
ORDER BY S.Age
'''

df = pd.read_sql_query(query, conn)
conn.close()

slider = alt.binding_range(min=df['Age'].min(), max=df['Age'].max(), step=1)
cutoff = alt.param(bind=slider, value=df['Age'].min())

predicate = alt.datum.Age < cutoff

chart = alt.Chart(df).mark_bar().encode(
    x='Age:O',
    y='NumStudents:Q',
    color=alt.when(predicate).then(alt.value("red")).otherwise(alt.value("blue")),
).add_params(
    cutoff
)

chart