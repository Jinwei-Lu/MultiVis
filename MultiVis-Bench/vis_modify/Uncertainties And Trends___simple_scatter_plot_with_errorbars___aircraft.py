import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/aircraft.sqlite')

query = '''
SELECT 
    CAST(REPLACE(Max_Gross_Weight, ',', '') AS REAL) AS Max_Gross_Weight,
    CAST(REPLACE(Total_disk_area, ',', '') AS REAL) AS Total_Disk_Area
FROM 
    aircraft
'''

df = pd.read_sql_query(query, conn)
conn.close()

df['yerr'] = df['Max_Gross_Weight'] * 0.1

base = alt.Chart(df).transform_calculate(
    ymin="datum.Max_Gross_Weight - datum.yerr",
    ymax="datum.Max_Gross_Weight + datum.yerr"
)

points = base.mark_point(
    filled=True,
    size=50,
    color='black'
).encode(
    x=alt.X('Total_Disk_Area:Q', title='Total Disk Area (sq ft)'),
    y=alt.Y('Max_Gross_Weight:Q', title='Max Gross Weight (lb)', scale=alt.Scale(zero=False))
)

errorbars = base.mark_errorbar().encode(
    x="Total_Disk_Area:Q",
    y="ymin:Q",
    y2="ymax:Q"
)

chart = points + errorbars

chart