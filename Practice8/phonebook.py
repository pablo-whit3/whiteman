import csv
import psycopg2
from config import dbhost, dbpassword, dbname, dbuser

conn = psycopg2.connect(
    host=dbhost,
    database=dbname,
    user=dbuser,
    password=dbpassword
)

def create_table():
    command = """CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(20) NOT NULL
            )"""
    with conn.cursor() as cur:
        cur.execute(command)
        conn.commit()

def print_contacts(contacts):
    if not contacts:
        print("  (no contacts)")
        return
    for contact in contacts:
        print(f" [{contact[0]}] {contact[1]} - {contact[2]}")

def get_contacts():
    print("Sorted by name/phone:")
    query = input()
    allowed = ["name", "phone"]
    
    if query not in allowed:
        print("Invalid option")
        return []
    
    command = f"SELECT * FROM contacts ORDER BY {query}"
    with conn.cursor() as cur:
        cur.execute(command)
        return cur.fetchall()
    
def search_contacts(pattern):
    command = "SELECT * FROM contacts WHERE name ILIKE %s OR phone ILIKE %s"
    like_pattern = f"%{pattern}%"
    with conn.cursor() as cur:
        cur.execute(command, (like_pattern, like_pattern))
        return cur.fetchall()

def insert(name,phone):
    command = "INSERT INTO contacts(name, phone) VALUES(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(command, (name, phone))
        conn.commit()

def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    insert(name,phone)
    print(f"Added a contact: {name} - {phone}")

def import_from_csv(file_csv):
    command = "INSERT INTO contacts(name, phone) VALUES(%s, %s)"
    with conn.cursor() as cur:
        with open(file_csv, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                name, phone = row
                cur.execute(command, (name, phone))
        conn.commit()
    print(f"Imported contacts from {file_csv}")

def update_phone(name, new_phone):
    command="UPDATE contacts SET phone = %s WHERE name = %s"
    with conn.cursor() as cur:
        cur.execute(command, (new_phone, name))
        conn.commit()
        print(f"Updated {cur.rowcount} row(s)")

def update_name(phone, new_name):
    command="UPDATE contacts SET name = %s WHERE phone = %s"
    with conn.cursor() as cur:
        cur.execute(command, (new_name, phone))
        conn.commit()
        print(f"Updated {cur.rowcount} row(s)")

def delete_by_name(name):
    command="DELETE FROM contacts WHERE name = %s"
    with conn.cursor() as cur:
        cur.execute(command, (name, ))
        conn.commit()
        print(f"Deleted {cur.rowcount} row(s)")

def delete_by_phone(phone):
    command="DELETE FROM contacts WHERE phone = %s"
    with conn.cursor() as cur:
        cur.execute(command, (phone, ))
        conn.commit()
        print(f"Deleted {cur.rowcount} row(s)")

def search_contacts_by_pattern(pattern):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_pattern(%s)", (pattern,))
        return cur.fetchall()
    
def get_contacts_paginated(limit, offset):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (limit, offset)
        )
        return cur.fetchall()

def insert_or_update(name, phone):
    with conn.cursor() as cur:
        cur.execute("CALL insert_or_update(%s, %s)", (name, phone))
        conn.commit()

def delete_user(value):
    with conn.cursor() as cur:
        cur.execute("CALL delete_user(%s)", (value,))
        conn.commit()

def insert_many(names, phones):
    with conn.cursor() as cur:
        cur.execute("CALL insert_many(%s, %s)", (names, phones))
        conn.commit()

def main():
    create_table()

    while True:
        print("\n--- Phonebook ---")
        print("1. Show all contacts")
        print("2. Add contacts")
        print("3. Import from csv")
        print("4. Search")
        print("5. Update phone by name")
        print("6. Update name by phone")
        print("7. Delete by name")
        print("8. Delete by phone")
        print("9. Search by pattern")
        print("10. Insert user")
        print("11. Insert many users")
        print("12. List contacts with pagination")
        print("13. Delete by name or phone")
        print("0. Exit")

        choice = input("\nChoice: ")

        if choice == "1":
            print_contacts(get_contacts())
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            filename=input("CSV file path: ")
            import_from_csv(filename)
        elif choice == "4":
            pattern=input("Search for: ")
            print_contacts(search_contacts(pattern))
        elif choice == "5":
            name = input("Name: ")
            new_phone = input("New phone: ")
            update_phone(name, new_phone)
        elif choice == "6":
            phone = input("Phone: ")
            new_name = input("New name: ")
            update_name(phone, new_name)
        elif choice == "7":
            name = input("Name:")
            delete_by_name(name)
        elif choice == "8":
            phone = input("Phone:")
            delete_by_phone(phone)
        elif choice == "9":
            pattern = input("Pattern:")
            contacts=search_contacts_by_pattern(pattern)
            print_contacts(contacts)
        elif choice == "10":
            name = input("Name:")
            phone = input("Phone:")
            insert_or_update(name,phone)
        elif choice == "11":
            n=input("Enter names separated by commas:")
            p=input("Enter phones separated by commas:")
            names=[ni.strip() for ni in n.split(",")]
            phones=[pi.strip() for pi in p.split(",")]
            insert_many(names,phones)
        elif choice == "12":
            limit = int(input("Show .. rows:"))
            offset = int(input("Skip .. rows:"))
            contacts=get_contacts_paginated(limit, offset)
            print_contacts(contacts)
        elif choice == "13":
            value = input("Name or phone:")
            delete_user(value)
        elif choice == "0":
            break
        else:
            print("invalid option")
    conn.close()
    print("Bye bye!")
if __name__ == "__main__":
    main()