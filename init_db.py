import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('First Product', 'Description for the first product', 'first', 100)
            )

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Second Product', 'Description for the second product', 'second', 200)
            )

connection.commit()
connection.close()