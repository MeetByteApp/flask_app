import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort, session


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
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


def get_cart():
    conn = get_db_connection()
    cart = conn.execute(
        "SELECT id, name, image, SUM(quantity), price, SUM(subTotal) FROM cart GROUP BY name").fetchall()
    conn.close()
    return cart


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
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    # Store id of the selected shirt
    id = int(request.args.get('id'))
    db.execute("DELETE FROM cart WHERE id = :id", id=id)
    # Select info of selected shirt from database
    goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
    # Extract values from selected shirt record
    # Check if shirt is on sale to determine price
    if (goods[0]["onSale"] == 1):
        price = goods[0]["onSalePrice"]
    else:
        price = goods[0]["price"]
    samplename = goods[0]["samplename"]
    image = goods[0]["image"]
    subTotal = qty * price
    # Insert selected shirt into shopping cart
    db.execute("INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)",
               id=id, qty=qty, samplename=samplename, image=image, price=price, subTotal=subTotal)
    shoppingCart = db.execute(
        "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
    shopLen = len(shoppingCart)
    # Rebuild shopping cart
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Go back to cart page
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


@app.route("/checkout/")
def checkout():
    conn = get_db_connection()
    order = conn.execute("SELECT * from cart")
    # Update purchase history of current customer
    for item in order:
        conn.execute("INSERT INTO purchases (uid, id, samplename, image, quantity) VALUES(:uid, :id, :samplename, :image, :quantity)",
                     uid=session["uid"], id=item["id"], samplename=item["samplename"], image=item["image"], quantity=item["qty"])
    # Clear shopping cart
    conn.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    conn = get_db_connection()
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    conn.execute("DELETE from cart WHERE id=:id", id=out)
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = db.execute(
        "SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


@app.route("/cart/")
def cart():
    # Clear shopping cart variables
    totItems, total, display = 0, 0, 0
    # Grab info currently in database
    cart = get_cart()
    print(cart)
    # Get variable values
    cartLen = len(cart)
    for i in range(cartLen):
        total += cart[i]["SUM(subTotal)"]
        totItems += cart[i]["SUM(quantity)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=cart, cartLen=cartLen, total=total, totItems=totItems, display=display, session=session)
