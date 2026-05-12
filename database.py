import sqlite3

class Database:
    def __init__(self):
        self.con = sqlite3.connect('users.db')
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS students(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id VARCHAR(20),
                         phone VARCHAR(20),
                         full_name VARCHAR(250)
                         );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name VARCHAR(250),
                         price INTEGER,
                         image VARCHAR(250),
                         count INTEGER
                         );
            """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cart(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id VARCHAR(20),
                            product_id INTEGER,
                            count INTEGER
                            );
            """)
        self.cur.execute("""                
            CREATE TABLE IF NOT EXISTS orders(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id VARCHAR(20),
                            products TEXT,
                            count INTEGER,
                            total_price INTEGER,
                            ordered_at DATETIME
                            );
        """)


    def add_user(self, user_id, phone, full_name):
        self.cur.execute("""INSERT INTO students (user_id, phone, full_name)
                         VALUES (?, ?, ?)""", (user_id, phone, full_name))
        self.con.commit()

    def check_user(self, user_id):
        return self.cur.execute("SELECT * FROM students WHERE user_id=?", (user_id,)).fetchone()
    
    def get_students(self):
        return self.cur.execute("SELECT * FROM students").fetchall()
    
    def get_student(self, id):
        return self.cur.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    
    def add_product(self, name, price, image, count):
        self.cur.execute("""INSERT INTO products (name, price, image, count)
                         VALUES (?, ?, ?, ?)""", (name, price, image, count))
        self.con.commit()

    def get_products(self):
        return self.cur.execute("SELECT * FROM products").fetchall()
    
    def get_product(self, id):
        return self.cur.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    
    def add_to_cart(self, user_id, product_id, count):
        product = self.get_product(product_id)
        if product and product[4] >= count:
            self.cur.execute("""INSERT INTO cart (user_id, product_id, count)
                            VALUES (?, ?, ?)""", (user_id, product_id, count))
        else:
            print(f"Maxsulot {product[1]} yetarli emas")
        
        self.con.commit()

    def get_cart(self, user_id):
        return self.cur.execute("SELECT * FROM cart WHERE user_id=?", (user_id,)).fetchall()
    
    def clear_cart(self, user_id):
        self.cur.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
        self.con.commit()

    def create_order(self, user_id, products, count, total_price):
        cart_items = self.get_cart(user_id)
        for item in cart_items:
            product_id = item[2]
            product = self.get_product(product_id)
            count = item[3]
            if product and product[4] >= count:
                self.cur.execute("UPDATE products SET count = count - ? WHERE id = ?", (count, product_id))
            else:
                print(f"Maxsulot {product[1]} yetarli emas")

        self.cur.execute("""INSERT INTO orders (user_id, products, count, total_price, ordered_at)
                         VALUES (?, ?, ?, ?, datetime('now'))""", (user_id, products, count, total_price))
        self.con.commit()