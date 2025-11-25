import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/election.sqlite')

query = '''
SELECT Zip_code, Population
FROM county
'''

df = pd.read_sql_query(query, conn)

conn.close()

chart = alt.Chart(df, title="Population Distribution by Zip Code", height=100, width=300).encode(
    alt.X("bin_Population_start:Q")
        .title("Population")
        .axis(grid=False),
    alt.X2("bin_Population_end:Q"),
    alt.Y("Zip_code:N").title("Zip Code"),
).transform_bin(
    ["bin_Population_start", "bin_Population_end"],
    field='Population',
    bin=alt.Bin(maxbins=20)
).transform_aggregate(
    count='count()',
    groupby=["Zip_code", "bin_Population_start", "bin_Population_end"]
).transform_calculate(
    y_offset="datum.count / 2",
    y2_offset="-datum.count / 2",
).mark_bar(xOffset=1, x2Offset=-1, cornerRadius=3).encode(
    alt.Color("count:Q")
        .title("Number of Counties")
        .scale(scheme="lighttealblue")
)

chart