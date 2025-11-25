import altair as alt
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/customer_deliveries.sqlite')

query = '''
SELECT
    CAST(strftime('%d', delivery_date) AS INTEGER) AS delivery_day_of_month,
    truck_id,
    delivery_status_code
FROM Order_Deliveries
'''

df = pd.read_sql_query(query, conn)
conn.close()

brush = alt.selection_interval()
brush_status = alt.when(brush).then("delivery_status_code")
base = alt.Chart(df).add_params(brush)

points = base.mark_point().encode(
    x=alt.X('delivery_day_of_month:Q', title='Delivery Day of Month'),
    y=alt.Y('truck_id:Q', title='Truck ID'),
    color=brush_status.otherwise(alt.value("grey")),
)

tick_axis = alt.Axis(labels=False, domain=False, ticks=False)
tick_color = brush_status.otherwise(alt.value("lightgrey"))

x_ticks = base.mark_tick().encode(
    alt.X('delivery_day_of_month:Q', axis=tick_axis),
    alt.Y('delivery_status_code:N', title='Delivery Status', axis=tick_axis),
    color=tick_color
)

y_ticks = base.mark_tick().encode(
    alt.X('delivery_status_code:N', title='', axis=tick_axis),
    alt.Y('truck_id:Q', axis=tick_axis),
    color=tick_color
)

y_ticks | (points & x_ticks)