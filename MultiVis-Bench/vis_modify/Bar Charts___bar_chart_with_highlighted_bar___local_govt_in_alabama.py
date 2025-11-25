import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/local_govt_in_alabama.sqlite')

query = '''
SELECT 
    P.Participant_Details AS Organizer,
    COUNT(E.Event_ID) AS Event_Count
FROM 
    Participants AS P
JOIN 
    Participants_in_Events AS PE ON P.Participant_ID = PE.Participant_ID
JOIN 
    Events AS E ON PE.Event_ID = E.Event_ID
WHERE 
    P.Participant_Type_Code = 'Organizer'
GROUP BY 
    P.Participant_Details
ORDER BY 
    Event_Count DESC
'''

df = pd.read_sql_query(query, conn)

conn.close()

highlighted_organizer = df.loc[df['Event_Count'].idxmax(), 'Organizer']

color = alt.when(alt.datum.Organizer == highlighted_organizer).then(alt.value("orange")).otherwise(alt.value("steelblue"))

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Organizer:N', title='Organizer'),
    y=alt.Y('Event_Count:Q', title='Number of Events Organized'),
    color=color
).properties(width=600, title="Number of Events Organized by Each Organizer")

chart