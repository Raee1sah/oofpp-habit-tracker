"""
seed_data.py

Populates the database with 5 predefined habits and 4 weeks of
synthetic completion data. This serves two purposes:

  1. It gives the application realistic example data to demonstrate
     its functionality without requiring manual data entry.
  2. It acts as a test fixture: the same generation logic is reused
     in the test suite to produce known, repeatable data for
     verifying the analytics functions.

Habits included (at least one daily, at least one weekly, per the
assignment's acceptance criteria):
  - Drink water          (daily)
  - Read for 20 minutes   (daily)
  - Exercise              (daily)
  - Weekly grocery shop    (weekly)
  - Clean the apartment    (weekly)
"""

from datetime import datetime, timedelta

from database import Database
from tracker import HabitTracker

PREDEFINED_HABITS = [
    ("Drink water", "daily"),
    ("Read for 20 minutes", "daily"),
    ("Exercise", "daily"),
    ("Weekly grocery shop", "weekly"),
    ("Clean the apartment", "weekly"),
]


def generate_completions(periodicity, weeks=4, break_streak=False):
    """
    Generate a list of synthetic completion datetimes spanning the
    given number of weeks, going backwards from now.

    :param periodicity: "daily" or "weekly".
    :param weeks: number of weeks of history to generate.
    :param break_streak: if True, skip one period partway through to
           produce a realistic broken streak (useful for testing).
    :return: list of datetime objects.
    """
    now = datetime.now()
    completions = []

    if periodicity == "daily":
        total_periods = weeks * 7
        step = timedelta(days=1)
    else:  # weekly
        total_periods = weeks
        step = timedelta(weeks=1)

    for i in range(total_periods):
        if break_streak and i == total_periods // 2:
            continue  # simulate a missed period
        completions.append(now - step * (total_periods - i))

    return completions


def seed_database(db_path="habits.db"):
    """
    Create/reset the database at db_path and populate it with the
    5 predefined habits and 4 weeks of completion data each.

    :param db_path: path to the SQLite database file.
    :return: the HabitTracker instance used, for further interaction.
    """
    database = Database(db_path)
    tracker = HabitTracker(database)

    for index, (task, periodicity) in enumerate(PREDEFINED_HABITS):
        habit = tracker.add_habit(task, periodicity)
        # Give one habit (index 2, "Exercise") a broken streak so the
        # analytics functions have realistic varied data to work with.
        break_streak = (index == 2)
        for completion_dt in generate_completions(periodicity, weeks=4, break_streak=break_streak):
            database.save_completion(habit.id, completion_dt.isoformat())

    return tracker


if __name__ == "__main__":
    seed_database()
    print("Database seeded with 5 predefined habits and 4 weeks of completion data.")
