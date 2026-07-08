import sqlite3


def create_database():

    conn = sqlite3.connect("nifty100.db")

    with open("db/schema.sql","r") as file:
        sql=file.read()

    conn.executescript(sql)

    conn.close()


if __name__=="__main__":
    create_database()
    print("Database created successfully")