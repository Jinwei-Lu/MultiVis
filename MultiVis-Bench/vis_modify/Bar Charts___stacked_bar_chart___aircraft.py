import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/aircraft.sqlite')

query = '''
SELECT 
    Airport_Name,
    International_Passengers AS Passengers,
    'International' AS Passenger_Type
FROM 
    airport
UNION ALL
SELECT 
    Airport_Name,
    Domestic_Passengers AS Passengers,
    'Domestic' AS Passenger_Type
FROM 
    airport
'''

df = pd.read_sql_query(query, conn)
conn.close()

chart = alt.Chart(df).mark_bar().encode(
    x='Airport_Name:N',
    y='sum(Passengers):Q',
    color='Passenger_Type:N'
)

chart.show()