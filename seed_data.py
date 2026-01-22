from db import get_connection, create_tables
from datetime import datetime, timedelta
import random

create_tables()

exercises = {
    "Bench Press": (30, 72),
    "Squat": (40, 110),
    "Deadlift": (50, 130),
    "Lat Pulldown": (25, 65),
    "Shoulder Press": (15, 45),
    "Bicep Curl": (6, 16),
    "Tricep Pushdown": (10, 30),
    "Leg Press": (80, 180),
}

conn = get_connection()
cur = conn.cursor()

start_date = datetime.now() - timedelta(days=180)  # 6 months
current = {k: v[0] for k, v in exercises.items()}
target = {k: v[1] for k, v in exercises.items()}

for day in range(180):
    date = start_date + timedelta(days=day)

    # Train 4 days/week
    if date.weekday() in [0, 2, 4, 6]:  # Mon, Wed, Fri, Sun
        todays = random.sample(list(exercises.keys()), random.randint(3, 5))

        for ex in todays:
            step = (target[ex] - exercises[ex][0]) / 180
            current[ex] += step

            # Rare small fatigue dip
            if random.random() < 0.05:
                current[ex] -= random.uniform(2, 5)

            # Plateau every ~3 weeks
            if day % 21 == 0 and random.random() < 0.3:
                current[ex] *= 0.97

            w = round(max(exercises[ex][0], min(current[ex], target[ex])) / 2) * 2

            sets = random.randint(3, 5)
            reps = random.choice([8, 10, 12])

            cur.execute(
                """
                INSERT INTO workouts (exercise, sets, reps, weight, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ex, sets, reps, w, date.strftime("%Y-%m-%d %H:%M:%S"))
            )

conn.commit()
conn.close()

print("Seeded 6 months of smooth, realistic gym progress!")