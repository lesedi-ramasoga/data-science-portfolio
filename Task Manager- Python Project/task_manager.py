import os
import datetime

# Created a dictionary to store all users and for easy checking.
# Load user data into a dictionary
user_data = {}
if os.path.exists("user.txt"):
    with open("user.txt", "r") as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(",")
                u = parts[0].strip()
                p = parts[1].strip()
                user_data[u] = p

tasks_list = []
if os.path.exists("tasks.txt"):
    with open("tasks.txt", "r") as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(",")
                tasks_list.append([part.strip() for part in parts])


def reg_user():
    '''
    Registers a new user by requesting a username and password.
    Checks if the username already exists in user_data to prevent duplicates.
    Writes the new user to 'user.txt' if passwords match.
    '''

    new_username = input("New Username: ")

    if new_username in user_data:
        print(
            "Error: This username already exists, please try a different one."
        )
        return

    new_password = input("New Password: ")

    confirm_password = input("Confirm Password: ")

    if new_password == confirm_password:
        with open("user.txt", "a") as out_file:
            out_file.write(f"\n{new_username}, {new_password}")

        user_data[new_username] = new_password
        print("New user added successfully!")

    else:
        print("Passwords do not match")


def add_task():
    '''
    Prompts the user for task details (assigned user, title, description,
    due date).
    Automatically captures the current date.
    Formats the data as a comma-separated string and appends it to 'tasks.txt'.
    '''
    user_name = input("Enter username of whom the task is assigned: ")
    title_task = input("Enter the title of the task: ")
    task_descript = input("Enter the task description: ")
    due_date = input(
        "Enter the due date (eg., 20 Oct 2023): "
    )
    current_date = datetime.date.today().strftime("%d %b %Y")

    task_line = (
        f"{user_name}, {title_task}, {task_descript}, "
        f"{current_date}, {due_date}, No"
    )
    with open("tasks.txt", "a") as file:
        file.write("\n" + task_line)
    tasks_list.append(
        [user_name, title_task, task_descript, current_date, due_date, "No"]
    )
    print("Task added successfully!")


def view_all():
    '''
    Iterates through the tasks_list and prints every task in a
    user-friendly, easy-to-read format to the console.
    '''
    for task_number, t in enumerate(tasks_list):
        print("----------------------------")
        print(f"Task number:       {task_number}")
        print(f"Task:              {t[1]}")
        print(f"Assigned to:       {t[0]}")
        print(f"Date assigned:     {t[3]}")
        print(f"Due date:          {t[4]}")
        print(f"Task complete?     {t[5]}")
        print(f"Task description:  {t[2]}")
        print("----------------------------")


def view_mine(username):
    '''
    Displays only the tasks assigned to the currently logged-in user.
    Allows the user to select a specific task to mark as complete
    or to edit the assigned username or due date (if not already complete).
    '''
    for i, t in enumerate(tasks_list):
        if t[0] == username:
            print(f"\nTask Number:   {i}")
            print(f"Task:          {t[1]}")
            print(f"Assigned to:   {t[0]}")
            print(f"Date assigned: {t[3]}")
            print(f"Due date:      {t[4]}")
            print(f"Task complete? {t[5]}")
            print(f"Description:   {t[2]}")

    while True:
        try:
            selection = int(input(
                "\nSelect a task number to edit or -1 to return: "
            ))

            if selection == -1:
                return

            if 0 <= selection < len(tasks_list):
                task = tasks_list[selection]
                if task[0] != username:
                    print("You can only edit tasks assigned to you.")
                    continue
                break

            else:
                print("That task number does not exist.")

        except ValueError:
            print("Invalid input. Please enter a numeric task number.")

    if task[5].strip() == "No":
        action = input("Enter 'c' to mark complete or 'e' to edit: ").lower()

        if action == 'c':
            task[5] = "Yes"

        elif action == 'e':
            new_user = input("New username (blank to skip): ")
            new_due = input("New due date (blank to skip): ")

            if new_user:
                task[0] = new_user
            if new_due:
                task[4] = new_due

        with open("tasks.txt", "w") as file:
            for t in tasks_list:
                file.write(", ".join(t).strip() + "\n")
        print("Task updated successfully.")
    else:
        print("Completed tasks cannot be edited.")


def view_completed():
    '''Displays all tasks that have been marked as "Yes" (completed).'''
    print("\n--- Completed Tasks ---")
    found = False
    for t in tasks_list:
        if t[5].strip() == "Yes":
            print(f"Task: {t[1]} | Assigned to: {t[0]}")
            found = True
    if not found:
        print("No completed tasks found.")


def delete_task():
    '''Allows the admin to delete a task by its index number.'''
    view_all()
    while True:
        try:
            selection = int(input(
                "\nEnter the task number to delete (or -1 to cancel): "
            ))
            if selection == -1:
                return
            if 0 <= selection < len(tasks_list):
                deleted = tasks_list.pop(selection)
                with open("tasks.txt", "w") as file:
                    for t in tasks_list:
                        file.write(", ".join(t).strip() + "\n")
                print(f"Task '{deleted[1]}' deleted successfully.")
                break
            else:
                print("Invalid task number.")
        except ValueError:
            print("Error: Please enter a valid integer.")


def generate_reports(tasks_list, user_data):
    '''
    Calculates statistics including total tasks, completion rates
    and user-specific metrics. Saves these summaries into 'task_overview.txt'
      and 'user_overview.txt'.
    '''
    total_tasks = len(tasks_list)
    curr_date = datetime.date.today()

    completed_tasks = sum(
        1 for task in tasks_list if task[5].strip() == "Yes"
    )
    incomplete_tasks = total_tasks - completed_tasks

    overdue_tasks = sum(
        1 for task in tasks_list
        if task[5].strip() == "No"
        and datetime.datetime.strptime(
            task[4], "%d %b %Y"
        ).date() < curr_date
    )

    with open("task_overview.txt", "w") as file:
        file.write(f"Total tasks: {total_tasks}\n")
        file.write(f"Completed tasks: {completed_tasks}\n")
        file.write(f"Incomplete tasks: {incomplete_tasks}\n")
        file.write(f"Incomplete and overdue tasks: {overdue_tasks}\n")

        if total_tasks > 0:
            file.write(
                f"Percentage incomplete: "
                f"{(incomplete_tasks / total_tasks) * 100:.2f}%\n"
            )
            file.write(
                f"Percentage overdue: "
                f"{(overdue_tasks / total_tasks) * 100:.2f}%\n"
            )
        else:
            file.write("Percentage incomplete: 0.00%\n")
            file.write("Percentage overdue: 0.00%\n")

    with open("user_overview.txt", "w") as file:
        file.write(f"Total users: {len(user_data)}\n")
        file.write(f"Total tasks: {total_tasks}\n")

        for user in user_data:
            u_tasks = [task for task in tasks_list if task[0] == user]
            number_of_tasks = len(u_tasks)

            file.write(f"\nUser: {user}\n")
            file.write(f"Tasks assigned: {number_of_tasks}\n")

            if number_of_tasks > 0:
                completed = sum(
                    1 for task in u_tasks if task[5].strip() == "Yes"
                )
                incomplete = number_of_tasks - completed

                overdue = sum(
                    1 for task in u_tasks
                    if task[5].strip() == "No"
                    and datetime.datetime.strptime(
                        task[4], "%d %b %Y"
                    ).date() < curr_date
                )

                file.write(
                    f"Percentage of total tasks: "
                    f"{(number_of_tasks / total_tasks) * 100:.2f}%\n"
                )
                file.write(
                    f"Percentage completed: "
                    f"{(completed / number_of_tasks) * 100:.2f}%\n"
                )
                file.write(
                    f"Percentage still incomplete: "
                    f"{(incomplete / number_of_tasks) * 100:.2f}%\n"
                )
                file.write(
                    f"Percentage incomplete and overdue: "
                    f"{(overdue / number_of_tasks) * 100:.2f}%\n"
                )
            else:
                file.write("No tasks assigned to this user.\n")


def display_statistics(tasks_list, user_data):
    '''
    Triggers the generation of report files and then reads their
    contents to display a summary of tasks and users directly
    in the terminal for the admin user.
    '''

    generate_reports(tasks_list, user_data)
    print("\n" + "-"*10)
    print("TASK OVERVIEW")
    print("-"*10)

    with open("task_overview.txt", "r") as f:
        print(f.read())

    print("\n" + "-"*10)
    print("USER OVERVIEW")
    print("-"*10)
    with open("user_overview.txt", "r") as f:
        print(f.read())

# Login section


logged_in = False

while not logged_in:
    print("Login Section:\n")
    user_input = input("Enter your username: ")
    pass_input = input("Enter your password: ")

    if (user_input.strip() in user_data
            and user_data[user_input.strip()] == pass_input.strip()):
        print("Login successful!")
        logged_in = True
    else:
        print("Invalid login credentials, please try again.")

# Main menu
while True:
    # Present the menu to the user and
    # make sure that the user input is converted to lower case.
    menu_prompt = "\nSelect one of the following options:\n"
    if user_input == 'admin':
        menu_prompt += "r  - register a user\n"
        menu_prompt += "a- add task\n"
        menu_prompt += "va- view all tasks\n"
        menu_prompt += "vm- view my tasks\n"
        menu_prompt += "vc- view all completed tasks\n"
        menu_prompt += "del- delete a task\n"
        menu_prompt += "ds - display statistics\n"
        menu_prompt += "gr - generate reports\ne  - exit\n: "

    else:
        menu_prompt += "a  - add task\n"
        menu_prompt += "va - view all tasks\n"
        menu_prompt += "vm - view my tasks\n"
        menu_prompt += "e  - exit\n: "

    menu = input(menu_prompt).lower()
    if menu == 'r' and user_input == 'admin':
        reg_user()
    elif menu == 'a':
        add_task()

    elif menu == 'va':
        view_all()

    elif menu == 'vm':
        view_mine(user_input)

    elif menu == 'vc' and user_input == 'admin':
        view_completed()

    elif menu == 'del' and user_input == 'admin':
        delete_task()

    elif menu == 'gr' and user_input == 'admin':
        generate_reports(tasks_list, user_data)

    elif menu == 'ds' and user_input == 'admin':
        display_statistics(tasks_list, user_data)

    elif menu == 'e':
        print("Goodbye!!!")
        exit()

