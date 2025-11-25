import altair as alt
from vega_datasets import data
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/course_teach.sqlite')
query = '''
SELECT C.Course_ID as IMDB_Rating, T.Teacher_ID as US_Gross, CA.Grade as Worldwide_Gross
FROM Course AS C
JOIN course_arrange AS CA ON C.Course_ID = CA.Course_ID
JOIN Teacher AS T ON CA.Teacher_ID = T.Teacher_ID;
'''
df = pd.read_sql_query(query, conn)
conn.close()

alt.Chart(df).mark_line().encode(
    alt.X("IMDB_Rating").bin(True),
    alt.Y(alt.repeat("layer"))
        .aggregate("mean")
        .title("Mean of US and Worldwide Gross"),
    color=alt.datum(alt.repeat("layer")),
).repeat(
    layer=["US_Gross", "Worldwide_Gross"]
)