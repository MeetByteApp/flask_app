import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Samsung S22', 'Samsung S22 Smartphone', 's22', 63999)
            )

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Nike Shoes', 'Nike casual shoes for men', 'shoes', 7999)
            )

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Laptop', 'Lenovo Yoga laptop', 'laptop', 93499)
            )

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Apple Watch', 'Apple Watch - smart watch', 'watch', 24999)
            )

cur.execute("INSERT INTO products (name, description, image, price) VALUES (?, ?, ?, ?)",
            ('Rich Dad Poor Dad', 'Self help book', 'book', 499)
            )

connection.commit()
connection.close()