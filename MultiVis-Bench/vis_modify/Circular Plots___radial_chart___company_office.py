import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/company_office.sqlite')

query = '''
SELECT 
    b.City AS city,
    o.move_in_year AS year,
    COUNT(o.company_id) AS company_count
FROM 
    Office_locations AS o
JOIN 
    buildings AS b ON o.building_id = b.id
GROUP BY 
    b.City, o.move_in_year
ORDER BY 
    b.City, o.move_in_year;
'''

df = pd.read_sql_query(query, conn)

conn.close()

base = alt.Chart(df).encode(
    alt.Theta("company_count:Q").stack(True),
    alt.Radius("company_count").scale(type="sqrt", zero=True, rangeMin=20),
    color="city:N",
    tooltip=["city:N", "year:Q", "company_count:Q"]
)

c1 = base.mark_arc(innerRadius=20, stroke="#fff")

c2 = base.mark_text(radiusOffset=10).encode(text="company_count:Q")

chart = c1 + c2

chart.properties(title="Companies Moving Into Buildings by City and Year")