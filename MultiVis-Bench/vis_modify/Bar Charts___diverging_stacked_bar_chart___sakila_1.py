import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/sakila_1.sqlite')

query = '''
SELECT 
    c.name AS category_name,
    f.rating,
    COUNT(*) AS count
FROM 
    film AS f
JOIN 
    film_category AS fc ON f.film_id = fc.film_id
JOIN 
    category AS c ON fc.category_id = c.category_id
GROUP BY 
    c.name, f.rating
ORDER BY 
    c.name, f.rating
'''

df = pd.read_sql_query(query, conn)
conn.close()

rating_order = {'G': -2, 'PG': -1, 'PG-13': 0, 'R': 1, 'NC-17': 2}
df['type_code'] = df['rating'].map(rating_order)

def compute_percentages(group):
    group = group.set_index('type_code').sort_index()
    perc = (group['count'] / group['count'].sum()) * 100
    group['percentage'] = perc
    group['percentage_end'] = perc.cumsum() - (perc[-2] + perc[-1] + perc[0] / 2)
    group['percentage_start'] = group['percentage_end'] - perc
    return group

df = df.groupby('category_name').apply(compute_percentages).reset_index(drop=True)

color_scale = alt.Scale(
    domain=['G', 'PG', 'PG-13', 'R', 'NC-17'],
    range=["#c30d24", "#f3a583", "#cccccc", "#94c6da", "#1770ab"]
)

y_axis = alt.Axis(title="Film Category", offset=5, ticks=False, minExtent=60, domain=False)

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("percentage_start:Q", title="Percentage"),
    x2="percentage_end:Q",
    y=alt.Y("category_name:N").axis(y_axis),
    color=alt.Color("rating:N").title("Rating").scale(color_scale)
)

chart.show()