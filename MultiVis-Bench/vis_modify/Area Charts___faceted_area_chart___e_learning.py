import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/e_learning.sqlite')

query = '''
SELECT 
    Subjects.subject_name AS subject,
    strftime('%Y-%m', Student_Course_Enrolment.date_of_completion) AS completion_month,
    COUNT(Student_Course_Enrolment.student_id) AS student_count
FROM 
    Student_Course_Enrolment
JOIN 
    Courses ON Student_Course_Enrolment.course_id = Courses.course_id
JOIN 
    Subjects ON Courses.subject_id = Subjects.subject_id
WHERE 
    Student_Course_Enrolment.date_of_completion IS NOT NULL
GROUP BY 
    Subjects.subject_name, completion_month
ORDER BY 
    Subjects.subject_name, completion_month;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_area().encode(
    x=alt.X("completion_month:T", title="Completion Month"),
    y=alt.Y("student_count:Q", title="Number of Students"),
    color=alt.Color("subject:N", title="Subject"),
    row=alt.Row("subject:N", title="Subject")
).properties(
    height=100,
    width=400
)

chart.show()