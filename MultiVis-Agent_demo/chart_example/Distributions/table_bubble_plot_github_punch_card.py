import altair as alt
import pandas as pd
import random
import datetime

num_points = 200
times = []
counts = []

for _ in range(num_points):
    start_date = datetime.datetime(2023, 1, 1)
    time_delta = datetime.timedelta(days=random.randint(0, 364), hours=random.randint(0, 23))
    random_time = start_date + time_delta
    times.append(random_time)
    counts.append(random.randint(1, 50))

hours = [t.hour for t in times]
days_of_week_num = [t.weekday() for t in times]
day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
days_of_week = [day_labels[d] for d in days_of_week_num]

df = pd.DataFrame({
    'hours': hours,
    'day_of_week': days_of_week,
    'counts': counts
})

chart = alt.Chart(df).mark_circle().encode(
    x='hours:O',
    y=alt.Y('day_of_week:O', sort=day_labels),
    size='counts:Q'
)

chart.show()