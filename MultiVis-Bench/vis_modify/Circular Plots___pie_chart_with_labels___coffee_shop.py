import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/coffee_shop.sqlite')

query = '''
SELECT Membership_card, COUNT(*) AS count
FROM member
GROUP BY Membership_card;
'''

df = pd.read_sql_query(query, conn)
conn.close()

base = alt.Chart(df).encode(
    alt.Theta("count:Q").stack(True),
    alt.Color("Membership_card:N").legend(None)
)

pie = base.mark_arc(outerRadius=120)
text = base.mark_text(radius=140, size=20).encode(text="Membership_card:N")

chart = pie + text

chart