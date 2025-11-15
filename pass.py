DATA_FILE = "passwords.txt"

# Read all data from the text file
def load_data():
    data = {}
    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    # split into at most 3 parts so password can contain commas
                    parts = line.split(",", 2)
                    if len(parts) == 3:
                        website, username, password = parts
                        data[website] = {"username": username, "password": password}
                    else:
                        # skip malformed lines
                        continue
    except FileNotFoundError:
        pass  # file does not exist yet
    return data

# Save the entire data dictionary back to the text file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        for website, info in data.items():
            line = f"{website},{info['username']},{info['password']}\n"
            f.write(line)

# Add a new entry
def add_entry(data):
    website = input("Enter website: ").strip()
    if not website:
        print("Website cannot be empty.\n")
        return

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    data[website] = {"username": username, "password": password}
    save_data(data)
    print("Saved successfully!\n")

# View all entries
def view_all(data):
    if not data:
        print("No data found.\n")
        return

    for site, info in data.items():
        print(f"Website: {site}")
        print(f"Username: {info['username']}")
        print(f"Password: {info['password']}")
        print("-" * 30)
    print()

# Search for a specific entry
def search(data):
    site = input("Enter website to search: ").strip()
    if site in data:
        print("\nEntry found:")
        print(f"Username: {data[site]['username']}")
        print(f"Password: {data[site]['password']}\n")
    else:
        print("No entry found for that website.\n")

# Update an existing entry
def update_entry(data):
    site = input("Enter website to update: ").strip()
    if site not in data:
        print("No entry found for that website.\n")
        return

    current = data[site]
    print("\nCurrent values (press Enter to keep):")
    print(f"Username: {current['username']}")
    print(f"Password: {current['password']}\n")

    new_username = input("New username: ").strip()
    new_password = input("New password: ").strip()

    if new_username:
        data[site]['username'] = new_username
    if new_password:
        data[site]['password'] = new_password

    save_data(data)
    print("Updated successfully!\n")

# Delete an entry
def delete_entry(data):
    site = input("Enter website to delete: ").strip()
    if site not in data:
        print("No entry found for that website.\n")
        return

    confirm = input(f"Are you sure you want to delete '{site}'? (y/N): ").strip().lower()
    if confirm == "y":
        del data[site]
        save_data(data)
        print("Deleted successfully.\n")
    else:
        print("Delete cancelled.\n")

# Main program loop
def main():
    data = load_data()

    while True:
        print("===== Password Manager (TXT Version) =====")
        print("1. Add New Password")
        print("2. View All")
        print("3. Search")
        print("4. Update")
        print("5. Delete")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_entry(data)
        elif choice == "2":
            view_all(data)
        elif choice == "3":
            search(data)
        elif choice == "4":
            update_entry(data)
        elif choice == "5":
            delete_entry(data)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
