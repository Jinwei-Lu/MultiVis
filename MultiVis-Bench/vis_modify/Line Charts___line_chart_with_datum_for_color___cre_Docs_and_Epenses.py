import altair as alt
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/cre_Docs_and_Epenses.sqlite')

query = """
SELECT
    Document_ID as IMDB_Rating,
    Project_ID * 100000 as US_Gross,
    Project_ID * 150000 as Worldwide_Gross
FROM Documents
LIMIT 10;
"""

df = pd.read_sql_query(query, conn)
conn.close()

alt.Chart(df).mark_line().encode(
    alt.X("IMDB_Rating:Q").bin(True),
    alt.Y(alt.repeat("layer"), type='quantitative')
        .aggregate("mean")
        .title("Mean of US and Worldwide Gross"),
    color=alt.datum(alt.repeat("layer")),
).repeat(
    layer=["US_Gross", "Worldwide_Gross"]
)