import csv
import psycopg2
import json
from config import dbhost, dbpassword, dbname, dbuser

conn = psycopg2.connect(
    host=dbhost,
    database=dbname,
    user=dbuser,
    password=dbpassword
)

def create_table():
    with open("schema.sql") as f:
        command = f.read()
    with conn.cursor() as cur:
        cur.execute(command)
    conn.commit()

#сортировка и вывод в терминал
def sorted_contacts():
    sorter = input("Sort by (name/birthday/date): ")

    map = {
        "name": "name",
        "birthday": "birthday",
        "date": "created_at"
    }

    if sorter not in map:
        print("Invalid")
        return

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS g_name, p.phone, p.type, c.created_at
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            ORDER BY {map[sorter]}
        """)
        print_contacts(cur.fetchall())

def print_contacts(contacts):
    if not contacts:
        print("(no contacts)")
        return
    for c in contacts:
        print(c)

#добавление контакта с терминала

def insert_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO groups(name)
            VALUES(%s)
            ON CONFLICT (name) DO NOTHING
        """, (group,))

        cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
        gid = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES(%s, %s, %s, %s)
            RETURNING id
        """, (name, email, birthday, gid))

        cid = cur.fetchone()[0]

        while True:
            phone = input("Phone (enter to stop): ")
            if not phone:
                break
            ptype = input("Type (home/work/mobile): ")
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES(%s, %s, %s)
            """, (cid, phone, ptype))

        conn.commit()
        print("Contact added!")

#импорт из csv
def import_from_csv():
    filename = input("Filename: ")
    with conn.cursor() as cur:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row["name"]
                email = row["email"]
                birthday = row["birthday"]
                group = row["group"]
                phone = row["phone"]
                ptype = row["type"]

                #проверяю контакт
                cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
                res = cur.fetchone()

                if res:
                    cid = res[0]
                else:
                    #создаю группу
                    cur.execute("""
                        INSERT INTO groups(name)
                        VALUES(%s)
                        ON CONFLICT DO NOTHING
                    """, (group,))

                    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
                    gid = cur.fetchone()[0]

                    #создаю контакт
                    cur.execute("""
                        INSERT INTO contacts(name, email, birthday, group_id)
                        VALUES(%s, %s, %s, %s)
                        RETURNING id
                    """, (name, email, birthday, gid))

                    cid = cur.fetchone()[0]

                #добавляю номер
                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES(%s, %s, %s)
                """, (cid, phone, ptype))

        conn.commit()

    print("CSV import completed!")

#поиск по паттерну в контактах

def search_contacts():
    pattern = input("Searching for: ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_pattern(%s)", (pattern,))
        print_contacts(cur.fetchall())

#вывод группы контактов

def filter_by_group():
    group = input("Group: ")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email
            FROM contacts c
            JOIN groups g ON c.group_id = g.id
            WHERE g.name = %s
        """, (group,))
        print_contacts(cur.fetchall())

#вывод даты по частям

def pagination():
    limit = int(input("How much to show: "))
    offset = int(input("How much to skip: "))

    while True:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_contacts_paginated(%s, %s)",
                (limit, offset)
            )
            data = cur.fetchall()

        print_contacts(data)

        cmd = input("next / prev / quit: ")

        if cmd == "next":
            offset += limit
        elif cmd == "prev":
            offset = max(0, offset - limit)
        elif cmd == "quit":
            break

#добавление телефона к контакту и перемещение в другую группу

def add_phone():
    name = input("Contact name: ")
    phone = input("Phone: ")
    ptype = input("Type: ")

    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()

def move_group():
    name = input("Contact name: ")
    group = input("New group: ")

    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()

#удаление контакта

def delete_user():
    value = input("Name or phone: ")
    with conn.cursor() as cur:
        cur.execute("CALL delete_user(%s)", (value,))
        conn.commit()

#джсоновские функции

def export_json():
    filename = input("Filename: ")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, c.email, c.birthday, g.name,
                   p.phone, p.type
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
        """)
        rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "name": r[0],
            "email": r[1],
            "birthday": str(r[2]),
            "group": r[3],
            "phone": r[4],
            "type": r[5]
        })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print("Exported!")

def import_json():
    filename = input("Filename: ")

    with open(filename) as f:
        data = json.load(f)

    for item in data:
        name = item["name"]

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
            exists = cur.fetchone()

        if exists:
            choice = input(f"{name} exists. skip/overwrite: ")
            if choice == "skip":
                continue
            elif choice == "overwrite":
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
                    conn.commit()

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO groups(name)
                VALUES(%s)
                ON CONFLICT DO NOTHING
            """, (item["group"],))

            cur.execute("SELECT id FROM groups WHERE name=%s", (item["group"],))
            gid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES(%s, %s, %s, %s)
                RETURNING id
            """, (name, item["email"], item["birthday"], gid))

            cid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES(%s, %s, %s)
            """, (cid, item["phone"], item["type"]))

            conn.commit()
    
    print("Imported!")

#меню

def main():
    create_table()
    while True:
        print("\n--- PHONEBOOK ---")
        print("1 Add contact")          #добавляю контакт
        print("2 Search")               #поиск на совпадение в контактах
        print("3 Filter by group")      #вывод всех контактов из одной группы
        print("4 Pagination")           #частичный вывод данных
        print("5 Add phone")            #добавляю телефон в контакт
        print("6 Move to group")        #перемещаю существующий контакт в новую группу
        print("7 Delete contact")       #удаляю контакт
        print("8 Export to JSON")       #загружаю в джсон
        print("9 Import from JSON")     #выгружаю из джсона
        print("10 Import from CSV")     #выгружаю из csv
        print("11 Show contacts sorted")
        print("0 Exit")                 #выход из менюшки   

        choice = input("Choice: ")

        if choice == "1":
            insert_contact()
        elif choice == "2":
            search_contacts()
        elif choice == "3":
            filter_by_group()
        elif choice == "4":
            pagination()
        elif choice == "5":
            add_phone()
        elif choice == "6":
            move_group()
        elif choice == "7":
            delete_user()
        elif choice == "8":
            export_json()
        elif choice == "9":
            import_json()
        elif choice == "10":
            import_from_csv()
        elif choice == "11":
            sorted_contacts()
        elif choice == "0":
            break
        else:
            print("Invalid")

    conn.close()

if __name__ == "__main__":
    main()