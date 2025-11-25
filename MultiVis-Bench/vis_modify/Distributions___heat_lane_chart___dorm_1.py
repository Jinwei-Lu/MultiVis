import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/dorm_1.sqlite')

query = '''
SELECT 
    Dorm.dorm_name AS dorm_name,
    Dorm.student_capacity AS capacity,
    Student.Age AS age
FROM 
    Lives_in
JOIN 
    Student ON Lives_in.stuid = Student.StuID
JOIN 
    Dorm ON Lives_in.dormid = Dorm.dormid
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df, title="Distribution of Student Ages Across Dorm Capacities", height=100, width=400).encode(
    alt.X("bin_Age_start:Q")
        .title("Student Age")
        .axis(grid=False),
    alt.X2("bin_Age_end:Q"),
    alt.Y("dorm_name:N").title("Dorm Name"),
    alt.Y2("y2"),
).transform_bin(
    ["bin_Age_start", "bin_Age_end"],
    field='age'
).transform_aggregate(
    count='count()',
    groupby=["bin_Age_start", "bin_Age_end", "dorm_name"]
).transform_bin(
    ["bin_count_start", "bin_count_end"],
    field='count'
).transform_calculate(
    y="datum.bin_count_end/2",
    y2="-datum.bin_count_end/2",
).transform_joinaggregate(
    max_bin_count_end="max(bin_count_end)",
)

layer1 = chart.mark_bar(xOffset=1, x2Offset=-1, cornerRadius=3).encode(
    alt.Color("max_bin_count_end:O")
        .title("Number of Students")
        .scale(scheme="lighttealblue")
)
layer2 = chart.mark_bar(xOffset=1, x2Offset=-1, yOffset=-3, y2Offset=3).encode(
    alt.Color("bin_count_end:O").title("Number of Students")
)

layer1 + layer2