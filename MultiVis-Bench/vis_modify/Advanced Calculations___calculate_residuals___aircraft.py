import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/aircraft.sqlite')

query = '''
SELECT 
    Aircraft, 
    CAST(REPLACE(Max_Gross_Weight, ',', '') AS REAL) AS Max_Gross_Weight,
    CAST(REPLACE(Total_disk_area, ' ft²', '') AS REAL) AS Total_Disk_Area
FROM 
    aircraft
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = (
    alt.Chart(df)
    .mark_point()
    .transform_joinaggregate(Average_Weight="mean(Max_Gross_Weight)")
    .transform_calculate(Weight_Residual="datum.Max_Gross_Weight - datum.Average_Weight")
    .encode(
        x=alt.X("Total_Disk_Area:Q").title("Total Disk Area (sq ft)"),
        y=alt.Y("Weight_Residual:Q").title("Weight Residual (lbs)"),
        color=alt.Color("Weight_Residual:Q").title("Weight Residual").scale(domainMid=0),
        tooltip=["Aircraft:N", "Max_Gross_Weight:Q", "Total_Disk_Area:Q"]
    )
    .properties(title="Aircraft Weight Residuals vs. Total Disk Area")
)

chart