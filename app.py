from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Clear old records (if any)
    cur.execute('DELETE FROM products')

    # Add NEW sample products (you can customize this!)
    products = [
        ("Lipstick", 199.0),
        ("Eyeliner", 149.0),
        ("Foundation", 399.0),
        ("Perfume", 699.0),
        ("Moisturizer", 249.0)
    ]
    cur.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)
    conn.commit()
    conn.close()
    
try:
    init_db()
except:
    pass

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    for pid, qty in cart.items():
        cur.execute("SELECT * FROM products WHERE id=?", (pid,))
        product = cur.fetchone()
        if product:
            name, price = product[1], product[2]
            subtotal = price * qty
            total += subtotal
            items.append({'id': pid, 'name': name, 'price': price, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total=total)

@app.route('/remove/<int:product_id>')
def remove(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)