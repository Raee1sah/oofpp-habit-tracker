"""
cli.py

Command-line interface for the habit tracker application. Provides a
simple interactive menu loop for creating, completing, deleting, and
analysing habits. No GUI is provided, per the project's acceptance
criteria, which focus on core backend functionality.
"""

from database import Database
from tracker import HabitTracker
from analytics import (
    get_all_habits,
    get_same_periodicity,
    longest_streak,
    overall_longest_streak,
)

MENU = """
==== Habit Tracker ====
1. Create a new habit
2. Complete a habit
3. List all habits
4. List habits by periodicity
5. Show longest streak for a habit
6. Show longest streak overall
7. Edit a habit
8. Delete a habit
9. Exit
"""


def _print_habits(habits):
    if not habits:
        print("No habits found.")
        return
    for h in habits:
        print(f"  [{h.id}] {h.task} ({h.periodicity}) - created {h.created_at}")


def run(db_path="habits.db"):
    """
    Start the interactive CLI loop.

    :param db_path: path to the SQLite database file to use.
    """
    database = Database(db_path)
    tracker = HabitTracker(database)

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            task = input("Habit description: ").strip()
            periodicity = input("Periodicity (daily/weekly): ").strip().lower()
            try:
                habit = tracker.add_habit(task, periodicity)
                print(f"Created habit [{habit.id}] {habit.task} ({habit.periodicity})")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            habit_id = input("Habit id to mark complete: ").strip()
            tracker.complete_habit(int(habit_id))
            print("Habit marked complete.")

        elif choice == "3":
            habits = get_all_habits(tracker.list_habits())
            _print_habits(habits)

        elif choice == "4":
            periodicity = input("Periodicity to filter by (daily/weekly): ").strip().lower()
            habits = get_same_periodicity(tracker.list_habits(), periodicity)
            _print_habits(habits)

        elif choice == "5":
            habit_id = int(input("Habit id: ").strip())
            habit = tracker.get_habit(habit_id)
            if habit is None:
                print("Habit not found.")
                continue
            completions = database.load_completions(habit_id)
            streak = longest_streak(completions, habit.periodicity)
            print(f"Longest streak for '{habit.task}': {streak}")

        elif choice == "6":
            habits = tracker.list_habits()
            completions_by_id = {h.id: database.load_completions(h.id) for h in habits}
            streak = overall_longest_streak(habits, completions_by_id)
            print(f"Longest streak across all habits: {streak}")

        elif choice == "7":
            habit_id = int(input("Habit id to edit: ").strip())
            existing = tracker.get_habit(habit_id)
            if existing is None:
                print("Habit not found.")
                continue
            print(f"Current: {existing.task} ({existing.periodicity})")
            new_task = input("New description (leave blank to keep current): ").strip()
            new_periodicity = input("New periodicity daily/weekly (leave blank to keep current): ").strip().lower()
            try:
                updated = tracker.update_habit(
                    habit_id,
                    task=new_task or None,
                    periodicity=new_periodicity or None
                )
                print(f"Updated habit [{updated.id}] {updated.task} ({updated.periodicity})")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "8":
            habit_id = int(input("Habit id to delete: ").strip())
            tracker.delete_habit(habit_id)
            print("Habit deleted.")

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Invalid option, please try again.")

    database.close()


if __name__ == "__main__":
    run()
