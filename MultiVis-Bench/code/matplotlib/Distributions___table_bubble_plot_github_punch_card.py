import matplotlib.pyplot as plt
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
days_of_week = [t.weekday() for t in times]

sizes = [c * 50 for c in counts]

plt.scatter(hours, days_of_week, s=sizes, alpha=0.6)

plt.xticks(range(24))
plt.xlabel('Hours of Day')

plt.yticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.ylabel('Day of Week')
plt.gca().invert_yaxis()

plt.show()