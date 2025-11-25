import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/customers_campaigns_ecommerce.sqlite')

query = '''
SELECT p.product_category, CAST(oi.item_order_quantity AS INTEGER) AS item_order_quantity
FROM Order_Items AS oi
JOIN Products AS p ON oi.product_id = p.product_id
'''

df = pd.read_sql_query(query, conn)

conn.close()

medians_df = df.groupby('product_category')['item_order_quantity'].median().reset_index()
medians_df.columns = ['product_category', 'median_quantity']
medians_df['lo'] = 'Low Quantity'
medians_df['hi'] = 'High Quantity'

y_axis = alt.Y("product_category").axis(
    title="Product Category",
    offset=50,
    labelFontWeight="bold",
    ticks=False,
    grid=True,
    domain=False,
)

base = alt.Chart(
    medians_df,
).encode(y_axis)

bubbles = (
    alt.Chart(df)
    .mark_circle(color="#6EB4FD")
    .encode(
        alt.X(
            "item_order_quantity:Q",
        ).title("Item Order Quantity"),
        y_axis,
        alt.Size("count()").legend(offset=75, title="Number of Orders"),
        tooltip=[alt.Tooltip("count()").title("Number of Orders")],
    )
)

ticks = base.mark_tick(color="black").encode(
    alt.X("median_quantity:Q")
    .axis(grid=False)
)

texts_lo = base.mark_text(align="right", x=-5).encode(text="lo")

texts_hi = base.mark_text(align="left", x=255).encode(text="hi")

chart = (bubbles + ticks + texts_lo + texts_hi).properties(
    title="Distribution of Item Order Quantities by Product Category", width=300, height=200
).configure_view(stroke=None)

chart