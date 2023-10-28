import sqlite3
import uuid
from flask import Flask, render_template, request, url_for, flash, redirect, abort, session


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_products(query=None):
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    if query:
        products = [product for product in products if query.lower()
                    in product['name'].lower()]
    conn.close()
    return products


def get_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?',
                           (product_id,)).fetchone()
    conn.close()
    if product is None:
        abort(404)
    return product


def add_to_cart(product_id, quantity):
    conn = get_db_connection()
    product = get_product(product_id)
    # Extract values from selected product record
    name = product["name"]
    image = product["image"]
    price = product["price"]
    subTotal = quantity * price
    # Insert selected product into shopping cart
    conn.cursor().execute("INSERT INTO cart (id, quantity, name, image, price, subTotal) VALUES ( ?, ?, ?, ?, ?, ?)",
                          (product_id, quantity, name, image, price, subTotal))
    conn.commit()
    conn.cursor().close()
    conn.close()


def delete_from_cart(product_id):
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM cart WHERE id = ?", (product_id,))
    conn.commit()
    conn.cursor().close()
    conn.close()


def get_cart():
    conn = get_db_connection()
    cart = conn.execute(
        "SELECT id, name, image, SUM(quantity), price, SUM(subTotal) FROM cart GROUP BY name").fetchall()
    conn.close()
    return cart


def clear_cart():
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM cart")
    conn.commit()
    conn.cursor().close()
    conn.close()


def create_order():
    conn = get_db_connection()
    cart = conn.execute("SELECT * FROM cart").fetchall()
    if (len(cart) > 0):
        order_id = str(uuid.uuid4())
        conn.cursor().execute("INSERT INTO orders (order_id, status, totalItems) VALUES( ?, ?, ?)",
                              (order_id, "Confirmed", len(cart)))
        for item in cart:
            conn.execute("INSERT INTO order_details (order_id, product_id, quantity, price) VALUES( ?, ?, ?, ?)",
                         (order_id, item["id"], item["quantity"], item["price"]))


app = Flask(__name__)


@app.route('/')
def products():
    products = get_products()
    productsLen = len(products)
    shoppingCart = []
    cartLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    return render_template('index.html', products=products, shoppingCart=shoppingCart, productsLen=productsLen, cartLen=cartLen, total=total, totItems=totItems, display=display)
    # if 'user' in session:
    #     shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
    #     shopLen = len(shoppingCart)
    #     for i in range(shopLen):
    #         total += shoppingCart[i]["SUM(subTotal)"]
    #         totItems += shoppingCart[i]["SUM(qty)"]
    #     shirts = db.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
    #     shirtsLen = len(shirts)
    #     return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    # return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route('/search')
def search():
    query = request.args.get('q')
    products = get_products(query)
    productsLen = len(products)
    shoppingCart = []
    cartLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    return render_template('index.html', products=products, shoppingCart=shoppingCart, productsLen=productsLen, cartLen=cartLen, total=total, totItems=totItems, display=display)


@app.route('/about')
def about_us():
    return render_template('about.html')


@app.route('/<int:id>/')
def product(id):
    product = get_product(id)
    return render_template('product.html', product=product)


@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    shoppingCart = []
    cartLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    # Store id of the selected product
    id = int(request.args.get('id'))
    # Select info of selected product from database
    add_to_cart(id, qty)
    shoppingCart = get_cart()
    cartLen = len(shoppingCart)
    # Rebuild shopping cart
    for i in range(cartLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(quantity)"]
    # Select all shirts for home page view
    products = get_products()
    productsLen = len(products)
    # Go back to home page
    return render_template("index.html", products=products, shoppingCart=shoppingCart, productsLen=productsLen, cartLen=cartLen, total=total, totItems=totItems, display=display)


@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    cartLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    # Store id of the selected shirt
    id = int(request.args.get('id'))
    delete_from_cart(id)
    add_to_cart(id, qty)
    shoppingCart = get_cart()
    cartLen = len(shoppingCart)
    # Rebuild shopping cart
    for i in range(cartLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(quantity)"]
    # Go back to cart page
    return render_template("cart.html", shoppingCart=shoppingCart, cartLen=cartLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():
    # Update purchase history of current customer
    create_order()
    # Clear shopping cart
    clear_cart()
    shoppingCart = []
    cartLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    conn = get_db_connection()
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    delete_from_cart(out)
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = get_cart()
    cartLen = len(shoppingCart)
    for i in range(cartLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(quantity)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, cartLen=cartLen, total=total, totItems=totItems, display=display)


@app.route("/cart/")
def cart():
    # Clear shopping cart variables
    totItems, total, display = 0, 0, 0
    # Grab info currently in database
    cart = get_cart()
    # Get variable values
    cartLen = len(cart)
    for i in range(cartLen):
        total += cart[i]["SUM(subTotal)"]
        totItems += cart[i]["SUM(quantity)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=cart, cartLen=cartLen, total=total, totItems=totItems, display=display)


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shirts ever bought by current user
    myShirts = db.execute(
        "SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShirtsLen = len(myShirts)
    # Render table with shopping history of current user
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)
