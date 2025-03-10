import requests
import getpass

BASE_URL = "https://sc23zyc.pythonanywhere.com/"
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

    url = input("Enter URL (default: https://sc23zyc.pythonanywhere.com/): ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    response = requests.post(f"{BASE_URL}/login/", json={
        "username": username,
        "password": password,
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
    while True:
        professor_id = input("Enter professor ID: ").strip()
        professor_info = requests.get(f"{BASE_URL}/professors/{professor_id}/")

        if professor_info.status_code == 200:
            professor_data = professor_info.json()
            professor_name = professor_data["name"]
            break
        elif professor_info.status_code == 404:
            print(f"Error: Professor with '{professor_id}' not found.")
        else:
            print("Error: Could not verify professor. Please try again.")
            return

    while True:
        module_code = input("Enter module code (e.g., CD1): ").strip()
        module_info = requests.get(f"{BASE_URL}/module/{module_code}/")

        if module_info.status_code == 200:
            module_data = module_info.json().get("modules", [])
            if module_data:
                module_name = module_data[0]["name"]
                break
            else:
                print("No module found with code '{module_code}'. Please try again.")
        elif module_info.status_code == 404:
            print(f"Error: Module with code '{module_code}' not found. Please try again.")
        else:
            print("Error: Could not verify module. Please try again.")
            return

    response = requests.get(f"{BASE_URL}/ratings/{professor_id}/modules/{module_code}/rating")

    if response.status_code == 200:
        data = response.json()

        print(f"The rating of {professor_name} ({professor_id}) in module {module_name} ({module_code}) is {data['rating']}")
    else:
        print("Error fetching rating:", response.json())

def rate_professor():
    if not TOKEN:
        print("You must log in first!")
        return

    while True:
        professor_id = input("Enter professor ID: ").strip()
        professor_info = requests.get(f"{BASE_URL}/professors/{professor_id}/")

        if professor_info.status_code == 200:
            professor_data = professor_info.json()
            professor_name = professor_data.get("name")
            break
        elif professor_info.status_code == 404:
            print(f"Error: Professor with '{professor_id}' not found.")
        else:
            print("Error: Could not verify professor. Please try again.")
            return

    while True:
        module_code = input("Enter module code: ").strip()

        try:
            year = int(input("Enter the year (e.g., 2018): ").strip())
            semester = int(input("Enter the semester (1 or 2): ").strip())
        except ValueError:
            print("Year and semester must be numbers. Please try again.")
            continue

        module_info = requests.get(f"{BASE_URL}/module/{module_code}/{year}/{semester}/")

        if module_info.status_code == 200:
            module_data = module_info.json()
            module_name = module_data.get("name", module_code)
            break
        elif module_info.status_code == 404:
            print(f"Error: No module found for {module_code}, {year}, Semester {semester}. Please try again.")
        else:
            print("Error: Could not verify module. Try again later.")
            return

    while True:
        try:
            rating = int(input("Enter rating (1-5): ").strip())


            if rating > 1 or rating < 5:
                break
            else:
                print("Rating must be between 1 and 5. Please try again.")
        except ValueError:
            print("Rating must be a number. Please try again.")

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

    headers = {
        "Authorization": f"Token {TOKEN}"
    }

    response = requests.post(f"{BASE_URL}/logout/", headers=headers)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Received invalid response from server")
        print("Raw response:", response.text)
        return

    if response.status_code == 200:
        TOKEN = None
        print("Logged out successfully!")
    else:
        print("Error:", data)
        print("Response status code:", response.status_code)
        print("Response headers:", response.headers)

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
