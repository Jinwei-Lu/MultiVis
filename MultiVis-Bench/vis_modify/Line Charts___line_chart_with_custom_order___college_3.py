import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/college_3.sqlite')

query = '''
SELECT 
    Course.CID AS CourseID,
    Course.CName AS CourseName,
    Enrolled_in.Grade,
    Gradeconversion.gradepoint AS GradePoint
FROM 
    Enrolled_in
JOIN 
    Course ON Enrolled_in.CID = Course.CID
JOIN 
    Gradeconversion ON Enrolled_in.Grade = Gradeconversion.lettergrade
WHERE 
    Course.DNO = 600
ORDER BY 
    Course.CID;
'''

df = pd.read_sql_query(query, conn)
conn.close()

grouped_df = df.groupby(['CourseID', 'CourseName'], as_index=False).agg({'GradePoint': 'mean'})

chart = alt.Chart(grouped_df).mark_line(point=True).encode(
    x=alt.X("CourseID:N").title("Course ID"),
    y=alt.Y("GradePoint:Q").title("Average Grade Points"),
    order="CourseID",
    tooltip=["CourseID", "CourseName", "GradePoint"]
).properties(
    title="Trend of Average Grade Points by Course in Computer Science Department"
)

chart