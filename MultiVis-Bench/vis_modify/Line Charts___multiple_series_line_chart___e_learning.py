import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/e_learning.sqlite')

query = '''
SELECT 
    Subjects.subject_name AS subject,
    strftime('%Y-%m', Student_Course_Enrolment.date_of_completion) AS completion_month,
    COUNT(Student_Course_Enrolment.registration_id) AS completions
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
    completion_month ASC;
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_line().encode(
    x=alt.X('completion_month:T', title='Completion Month'),
    y=alt.Y('completions:Q', title='Number of Completions'),
    color=alt.Color('subject:N', title='Subject')
).properties(
    title='Number of Course Completions Over Time by Subject'
)

chart.show()