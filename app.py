#!python3
import os
import re
import hashlib
from datetime import datetime
from colorama import Fore, Style
from getpass import getpass
from prettytable import PrettyTable


# Colors
def green(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")


def red(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def yellow(text):
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")


def blue(text):
    print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")


def magenta(text):
    print(f"{Fore.MAGENTA}{text}{Style.RESET_ALL}")


def cyan(text):
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")


USERS_FILE = 'users.csv'
PROJECTS_FILE = 'projects.csv'
if not os.path.exists(USERS_FILE):
    open(USERS_FILE, 'a').close()
if not os.path.exists(PROJECTS_FILE):
    open(PROJECTS_FILE, 'a').close()

# Regex to validate Egyptian phone numbers
phone_regex = re.compile(r'^(\+2)?01[0125][0-9]{8}$')

# Helper functions

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

"""Hashes the given password using SHA256."""
hash_password = lambda password: hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Loads the users data from the text file."""
    users = []
    with open(USERS_FILE, 'r') as file:
        for line in file:
            id, first_name, last_name, email, password_hash, phone_number = line.strip().split(',')
            users.append({
                'id': int(id),
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password_hash': password_hash,
                'phone_number': phone_number
            })
    return users


def save_users(users):
    """Saves the users data to the text file."""
    with open(USERS_FILE, 'w') as file:
        for user in users:
            file.write(f"{user['id']},{user['first_name']},{user['last_name']},"
                       f"{user['email']},{user['password_hash']},{user['phone_number']}\n")


def load_projects():
    """Loads the projects data from the text file."""
    projects = []
    with open(PROJECTS_FILE, 'r') as file:
        for line in file:
            id, title, details, target, start_time_str, end_time_str, owner_id = line.strip().split(',')
            projects.append({
                'id': int(id),
                'title': title,
                'details': details,
                'target': float(target),
                'start_time': datetime.fromisoformat(start_time_str),
                'end_time': datetime.fromisoformat(end_time_str),
                'owner_id': int(owner_id)
            })
    return projects


def save_projects(projects):
    """Saves the projects data to the text file."""
    with open(PROJECTS_FILE, 'w') as file:
        for project in projects:
            file.write(f"{project['id']},{project['title']},{project['details']},"
                       f"{project['target']},{project['start_time'].isoformat()},"
                       f"{project['end_time'].isoformat()},{project['owner_id']}\n")


def validate_date(date_str):
    """Validates a date string in the format yyyy-mm-dd."""
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


# Authentication system

def register():
    """Registers a new user."""
    yellow("Registration")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    email = input("Email: ")
    password = getpass("Password: ")
    confirm_password = getpass("Confirm password: ")
    phone_number = input("Phone number: ")

    # Validation
    errors = []
    if not first_name:
        errors.append('First name is required.')
    if not last_name:
        errors.append('Last name is required.')
    if not email:
        errors.append('Email is required.')
    # elif not re.match(r'^\S+@\S+\.\S+$', email):
    elif not re.match(r'^[a-zA-z][a-zA-z1-9._]+@[a-zA-z-]+\.[a-z]{2,}(\.[a-z]{2,})?$', email):
        errors.append('Invalid email format.')
    elif any(user['email'] == email for user in load_users()):
        errors.append('Email already registered.')
    if not password:
        errors.append('Password is required.')
    elif password != confirm_password:
        errors.append('Passwords do not match.')
    if not phone_number:
        errors.append('Phone number is required.')
    elif not phone_regex.match(phone_number):
        errors.append('Invalid phone number format.')

    if errors:
        red("Registration failed. Please fix the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        # Hash password
        password_hash = hash_password(password)

        # Generate user ID
        users = load_users()
        user_id = max(user['id'] for user in users) + 1 if users else 1

        # Add user to file
        users.append({
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password_hash': password_hash,
            'phone_number': phone_number
        })
        save_users(users)

        green("Registration successful. Please login to continue.")


def login():
    """Logs in a user."""
    yellow("Login")
    email = input("Email: ")
    password = getpass("Password: ")

    # Find user by email
    user = next((user for user in load_users() if user['email'] == email), None)

    if user and user['password_hash'] == hash_password(password):
        green("Login successful.")
        return user
    else:
        red("Invalid email or password.")
        return None


# Projects

def create_project(user):
    """Creates a new project."""
    yellow("Create project")

    title = input("Title: ")
    details = input("Details: ")
    target_str = input("Total target: ")

    start_time_str = input("Start time (yyyy-mm-dd): ")
    end_time_str = input("End time (yyyy-mm-dd): ")

    # Validation
    errors = []
    if not title:
        errors.append('Title is required.')
    if not details:
        errors.append('Details are required.')
    if not target_str:
        errors.append('Total target is required.')
    else:
        try:
            target = float(target_str)
            if target <= 0:
                raise ValueError
        except ValueError:
            errors.append('Invalid total target.')
    if not start_time_str:
        errors.append('Start time is required.')
    elif not validate_date(start_time_str):
        errors.append('Invalid start time format.')
    if not end_time_str:
        errors.append('End time is required.')
    elif not validate_date(end_time_str):
        errors.append('Invalid end time format.')
    elif datetime.fromisoformat(start_time_str) >= datetime.fromisoformat(end_time_str):
        errors.append('End time must be after start time.')

    if errors:
        red("Project creation failed. Please fix the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        # Generate project ID
        projects = load_projects()
        project_id = max(project['id'] for project in projects) + 1 if projects else 1

        # Add project to file
        projects.append({
            'id': project_id,
            'title': title,
            'details': details,
            'target': float(target_str),
            'start_time': datetime.fromisoformat(start_time_str),
            'end_time': datetime.fromisoformat(end_time_str),
            'owner_id': user['id']
        })
        save_projects(projects)

        green("Project created successfully.")


def view_projects():
    """Displays all projects."""
    projects = load_projects()
    if projects:
        print("Projects")
        prettytable = PrettyTable()
        prettytable.field_names = ["ID", "Title", "Details", "Total target", "Start time", "End time", "Owner"]
        for project in projects:
            owner = next((user for user in load_users() if user['id'] == project['owner_id']), None)
            owner = f"{owner['first_name']} {owner['last_name']} ({project['owner_id']})" if owner else "N/A"
            prettytable.add_row([
                project['id'],
                project['title'],
                project['details'],
                project['target'],
                project['start_time'].strftime('%Y-%m-%d'),
                project['end_time'].strftime('%Y-%m-%d'),
                owner
            ])
        print(prettytable)
    else:
        red("No projects found.")


def list_project_ids(user):
    """Lists all project IDs."""
    projects = load_projects()
    return [project['id'] for project in projects if project['owner_id'] == user['id']]


def edit_project(user):
    """Edits an existing project."""
    yellow("Edit project")

    # Find project by ID
    ids = list_project_ids(user)
    project_id = input(f"Project ID {ids}: ")
    project = next((project for project in load_projects() if project['id'] == int(project_id)), None)

    if not project:
        red("Project not found.")
        return

    if project['id'] not in ids:  # project['owner_id'] != user['id']:
        red("You do not have permission to edit this project.")
        return

    # Get updated details
    cyan('Leave blank to keep existing value')
    title = input(f"Title ({project['title']}): ")
    details = input(f"Details ({project['details']}): ")
    target_str = input(f"Total target ({project['target']}): ")
    start_time_str = input(f"Start time ({project['start_time'].strftime('%Y-%m-%d')}): ")
    end_time_str = input(f"End time ({project['end_time'].strftime('%Y-%m-%d')}): ")

    # Validation
    errors = []
    if title:
        project['title'] = title
    if details:
        project['details'] = details
    if target_str:
        try:
            target = float(target_str)
            if target <= 0:
                raise ValueError
            project['target'] = target
        except ValueError:
            errors.append('Invalid total target.')
    if start_time_str:
        if not validate_date(start_time_str):
            errors.append('Invalid start time format.')
        else:
            project['start_time'] = datetime.fromisoformat(start_time_str)
    if end_time_str:
        if not validate_date(end_time_str):
            errors.append('Invalid end time format.')
        else:
            end_time = datetime.fromisoformat(end_time_str)
            if project['start_time'] >= end_time:
                errors.append('End time must be after start time.')
            else:
                project['end_time'] = end_time

    if errors:
        red("Project update failed. Please fix the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        save_projects(load_projects())
        green("Project updated successfully.")
        return True


def delete_project(user):
    """Deletes an existing project."""
    yellow("Delete project")

    # Find project by ID
    project_id = input("Project ID: ")
    project = next((project for project in load_projects() if project['id'] == int(project_id)), None)

    if not project:
        print("Project not found.")
        return

    if project['owner_id'] != user['id']:
        print("You do not have permission to delete this project.")
        return

    load_projects().remove(project)
    save_projects(load_projects())

    green("Project deleted successfully.")
    return True


def search_project():
    """Searches for a project by start/end time."""
    yellow("Search project")

    start_time_str = input("Start time (required): ")
    end_time_str = input("End time (optional): ")

    # Validation
    errors = []
    if not validate_date(start_time_str):
        errors.append('Invalid start time format.')
    else:
        start_time = datetime.fromisoformat(start_time_str)
    if end_time_str and not validate_date(end_time_str):
        errors.append('Invalid end time format.')
    elif end_time_str:
        end_time = datetime.fromisoformat(end_time_str)

    if errors:
        red("Search failed. Please fix the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        projects = [project for project in load_projects()
                    if project['start_time'] >= start_time
                    and (not end_time_str or project['end_time'] <= end_time)]
        if projects:
            green(f"Found {len(projects)} project(s):")
            view_projects()
        else:
            red("No projects found.")


current_user = None
# Main loop
while True:
    clear()
    cyan("Welcome to Fundraise!")
    if not current_user:
        yellow("1. Register")
        yellow("2. Login")
    else:
        blue("3. Create project")
        blue("4. View projects")
        blue("5. Edit project")
        blue("6. Delete project")
        blue("7. Search project")
    red("8. Quit")

    choice = input("Enter your choice: ")
    if not choice or choice not in list('12345678'):
        print("Invalid choice.")
        continue
    elif current_user and choice in ['1', '2']:
        print("Please logout first.")
    elif not current_user and choice in ['3', '4', '5', '6', '7']:
        print("Please login first.")
    else:
        if choice == '1':
            register()
        elif choice == '2':
            user = login()
            if user:
                print(f"Welcome {user['first_name']}!")
                current_user = user
        elif choice == '3':
            if not current_user:
                print("Please login first.")
            else:
                create_project(current_user)
        elif choice == '4':
            view_projects()
        elif choice == '5':
            if not current_user:
                print("Please login first.")
            else:
                edit_project(current_user)
        elif choice == '6':
            if not current_user:
                print("Please login first.")
            else:
                delete_project(current_user)
        elif choice == '7':
            search_project()
        elif choice == '8':
            print("Thank you for using Fundraise!")
            break
        else:
            print("Invalid choice. Please try again.")
    os.system('pause')
