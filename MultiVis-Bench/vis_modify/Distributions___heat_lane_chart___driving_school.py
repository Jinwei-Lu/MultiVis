import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/driving_school.sqlite')
query = '''
SELECT 
    Vehicles.vehicle_details AS vehicle_type, 
    Lessons.price AS lesson_price
FROM 
    Lessons
JOIN 
    Vehicles ON Lessons.vehicle_id = Vehicles.vehicle_id
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df, title="Distribution of Lesson Prices by Vehicle Type", height=100, width=300).encode(
    alt.X("bin_price_start:Q")
        .title("Lesson Price")
        .axis(grid=False),
    alt.X2("bin_price_end:Q"),
    alt.Y("vehicle_type:N").title("Vehicle Type"),
    alt.Y2("y2"),
).transform_bin(
    ["bin_price_start", "bin_price_end"],
    field='lesson_price',
    bin=alt.Bin(maxbins=20)
).transform_aggregate(
    count='count()',
    groupby=["vehicle_type", "bin_price_start", "bin_price_end"]
).transform_bin(
    ["bin_count_start", "bin_count_end"],
    field='count'
).transform_calculate(
    y="datum.bin_count_end/2",
    y2="-datum.bin_count_end/2",
).transform_joinaggregate(
    max_bin_count_end="max(bin_count_end)",
    groupby=["vehicle_type"]
)

layer1 = chart.mark_bar(xOffset=1, x2Offset=-1, cornerRadius=3).encode(
    alt.Color("max_bin_count_end:O")
        .title("Number of Lessons")
        .scale(scheme="lighttealblue")
)
layer2 = chart.mark_bar(xOffset=1, x2Offset=-1, yOffset=-3, y2Offset=3).encode(
    alt.Color("bin_count_end:O").title("Number of Lessons")
)

layer1 + layer2