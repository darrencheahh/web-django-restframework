import requests
import getpass

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None

def register():
    username = input("Enter username:")
    email = input("Enter email:")
    password = getpass.getpass("Enter password:")

    response = requests.post(f"{BASE_URL}/register/", json={
        "username": username,
        "email": email,
        "password": password
    })

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Received an invalid response from server")
        print("Raw response:", response.text)
        return

    if response.status_code == 201:
        print("User registered successfully")
    else:
        print("Error registering user", data)

def login():
    global TOKEN

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    response = requests.post(f"{BASE_URL}/login/", json={
        "username": username,
        "password": password
    })

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Received an invalid response from server")
        print("Raw response:", response.text)
        return

    if response.status_code == 200:
        TOKEN = response.json()["token"]
        print("Login successful!")
    else:
        print("Login failed:", data)

def list_module():
    response = requests.get(f"{BASE_URL}/modules/")

    if response.status_code == 200:
        modules = response.json()
        print("\nModules Available:")
        print("{:<10} {:<30} {:<5} {:<5} {:<20}".format("Code", "Name", "Year", "Sem", "Taught By"))
        print("-" * 80)
        for module in modules:
            professors = ", ".join([professor["name"] for professor in module["professors"]])
            print("{:<10} {:<30} {:<5} {:<5} {:<20}".format(module["code"], module["name"], module["year"], module["semester"], professors))
    else:
        print("Error fetching modules:", response.json())


def view_professor_ratings():
    response = requests.get(f"{BASE_URL}/ratings/")

    if response.status_code == 200:
        ratings = response.json()
        print("\nProfessor Ratings:")
        for entry in ratings:
            print(f"{entry['professor']}: {entry['rating']}")
    else:
        print("Failed to fetch professor ratings:", response.json())

def avg_rating():
    professor_id = input("Enter professor ID: (e.g., JE1): ").strip()
    module_code = input("Enter module code (e.g., CD1): ").strip()

    response = requests.get(f"{BASE_URL}/ratings/{professor_id}/modules/{module_code}/rating")

    if response.status_code == 200:
        data = response.json()

        professor_name = '-'
        module_name = '-'

        professor_info = requests.get(f"{BASE_URL}/professors/{professor_id}/")
        if professor_info.status_code == 200:
            professor_data = professor_info.json()
            if "name" in professor_data:
                professor_name = professor_data["name"]

        module_info = requests.get(f"{BASE_URL}/module/{module_code}/")
        if module_info.status_code == 200:
            module_data = professor_info.json()
            if "name" in module_data:
                module_name = module_data["name"]

        print(f"The rating of {professor_name} ({professor_id} in module {module_name} ({module_code}) is {data['rating']}")
    else:
        print("Error fetching rating:", response.json())

def rate_professor():
    if not TOKEN:
        print("You must log in first!")
        return

    professor_id = input("Enter professor ID: ")
    module_code = input("Enter module code: ")
    try:
        year = int(input("Enter the year (e.g., 2018): ").strip())
        semester = int(input("Enter the semester (1 or 2): ").strip())
        rating = int(input("Enter the rating (1-5): ").strip())
    except ValueError:
        print("Year, semester and rating must be numbers")

    if rating < 1 or rating > 5:
        print("Rating must be between 1 and 5")
        return

    headers = {
        "Authorization" : f"Token {TOKEN}"
    }

    response = requests.post(
        f"{BASE_URL}/rate/",
        headers=headers,
        json={
            "professor_id": professor_id,
            "module_code": module_code,
            "year": year,
            "semester": semester,
            "rating": rating}
    )

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Received invalid response from server")
        print("Raw response:", response.text)
        return

    if response.status_code == 201:
        print("Rating submitted successfully!")
    else:
        print("Error:", data)

def logout():
    global TOKEN
    if not TOKEN:
        print("You are not logged in!")
        return

    response = requests.post(f"{BASE_URL}/logout/", headers={"Authorization": f"Token {TOKEN}"})

    if response.status_code == 200:
        TOKEN = None
        print("Logged out successfully!")
    else:
        print("Error:", response.json())

def main():
    while True:
        print("\nCommand Options:")

        if TOKEN:
            print("Logout - 'logout'")
            print("Rate Professor - 'rate'")
        else:
            print("Register - 'register'")
            print("Login - 'login'")

        print("List Modules - 'list'")
        print("View All Professor Ratings - 'view'")
        print("View Average Rating - 'average'")
        print("Exit - 'exit'")

        choice = input("Enter option: ").strip()

        if choice == "register":
            register()
        elif choice == "login":
            login()
        elif choice == "list":
            list_module()
        elif choice == "view":
            view_professor_ratings()
        elif choice == "average":
            avg_rating()
        elif choice == "rate":
            rate_professor()
        elif choice == "logout":
            logout()
        elif choice == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again")

if __name__ == "__main__":
    main()
