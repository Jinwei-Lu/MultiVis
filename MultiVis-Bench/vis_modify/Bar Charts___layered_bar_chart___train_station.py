import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/train_station.sqlite')
query = '''
SELECT 
    Name AS Station_Name,
    Annual_entry_exit AS Entry_Exit,
    Annual_interchanges AS Interchanges
FROM 
    station
WHERE 
    Location = 'London'
'''
df = pd.read_sql_query(query, conn)
conn.close()

df_melted = df.melt(id_vars='Station_Name', value_vars=['Entry_Exit', 'Interchanges'], 
                    var_name='Traffic_Type', value_name='Passenger_Count')
chart = alt.Chart(df_melted).mark_bar(opacity=0.7).encode(
    x='Station_Name:N',
    y=alt.Y('Passenger_Count:Q').stack(None),
    color='Traffic_Type:N'
)

chart