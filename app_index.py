import os
import sqlite3
from flask import Flask, request, jsonify, render_template

# Setup template & static folders reliably for both local and Vercel serverless
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# Fallback rich catalog metadata
ITEM_METADATA = {
    'Biriyani': {
        'category': 'Biryani',
        'is_veg': False,
        'rating': 4.8,
        'rating_count': 1250,
        'prep_time': '25-30 min',
        'description': 'Aromatic long-grain basmati rice layered with marinated tender cuts, fragrant saffron, and caramelized onions.',
        'image': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=700&q=80',
        'badge': 'Bestseller'
    },
    'Paneer': {
        'category': 'Vegetarian',
        'is_veg': True,
        'rating': 4.6,
        'rating_count': 890,
        'prep_time': '20-25 min',
        'description': 'Fresh cottage cheese cubes cooked in a velvety tomato-cashew makhani gravy with aromatic spices.',
        'image': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=700&q=80',
        'badge': 'Chef Choice'
    },
    'Butter Chicken': {
        'category': 'Non-Vegetarian',
        'is_veg': False,
        'rating': 4.9,
        'rating_count': 2400,
        'prep_time': '30-35 min',
        'description': 'Tender charcoal-grilled chicken in a rich, buttery, mildly sweet and savory spiced tomato sauce.',
        'image': 'https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?auto=format&fit=crop&w=700&q=80',
        'badge': 'Must Try'
    },
    'Garlic Naan': {
        'category': 'Breads',
        'is_veg': True,
        'rating': 4.7,
        'rating_count': 640,
        'prep_time': '15-20 min',
        'description': 'Traditional clay oven baked flatbread brushed with crushed roasted garlic, cilantro, and butter.',
        'image': 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=700&q=80',
        'badge': 'Popular'
    },
    'Chicken Tikka': {
        'category': 'Non-Vegetarian',
        'is_veg': False,
        'rating': 4.8,
        'rating_count': 1100,
        'prep_time': '20-25 min',
        'description': 'Smoky char-grilled chicken morsels marinated in spiced tandoori yogurt and mint glaze.',
        'image': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=700&q=80',
        'badge': 'Hot & Spicy'
    },
    'Gulab Jamun': {
        'category': 'Desserts',
        'is_veg': True,
        'rating': 4.9,
        'rating_count': 780,
        'prep_time': '10-15 min',
        'description': 'Warm, golden khoya milk dumplings soaked in cardamom and rose water infused sugar syrup.',
        'image': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=700&q=80',
        'badge': 'Sweet Tooth'
    },
    'Veg Pulao': {
        'category': 'Vegetarian',
        'is_veg': True,
        'rating': 4.5,
        'rating_count': 420,
        'prep_time': '20-25 min',
        'description': 'Fragrant basmati rice tossed with garden-fresh green peas, carrots, beans, and whole spices.',
        'image': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=700&q=80',
        'badge': 'Healthy'
    },
    'Masala Dosa': {
        'category': 'Vegetarian',
        'is_veg': True,
        'rating': 4.7,
        'rating_count': 950,
        'prep_time': '15-20 min',
        'description': 'Crispy golden fermented crepe stuffed with spiced potato masala, served with coconut chutney & sambar.',
        'image': 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=700&q=80',
        'badge': 'South Special'
    }
}

def init_sqlite_db(conn):
    """Initialize SQLite schema and seed initial data if needed."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            category_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            delivery_address TEXT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Seed default items if empty
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        default_items = [
            (4, 'Biriyani', 150.00, 2),
            (5, 'Paneer', 100.00, 1),
            (6, 'Butter Chicken', 200.00, 2),
            (7, 'Garlic Naan', 50.00, 1),
            (8, 'Chicken Tikka', 220.00, 2),
            (9, 'Gulab Jamun', 80.00, 1),
            (10, 'Veg Pulao', 130.00, 1),
            (11, 'Masala Dosa', 90.00, 1)
        ]
        cursor.executemany("INSERT OR REPLACE INTO items (item_id, item_name, price, category_id) VALUES (?, ?, ?, ?)", default_items)
        conn.commit()

def create_connection():
    """
    Connect to MySQL database when available (e.g. local environment),
    or gracefully fall back to SQLite (e.g. Vercel serverless / cloud deployments).
    """
    # Check if MySQL can be reached
    try:
        import mysql.connector
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_user = os.getenv('MYSQL_USER', 'root')
        mysql_password = os.getenv('MYSQL_PASSWORD', 'root')
        mysql_database = os.getenv('MYSQL_DATABASE', 'zomato')
        mysql_port = int(os.getenv('MYSQL_PORT', 3307))

        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            port=mysql_port,
            connection_timeout=2
        )
        return conn, 'mysql'
    except Exception:
        # Fall back to SQLite database
        db_dir = os.path.join(BASE_DIR, 'db')
        os.makedirs(db_dir, exist_ok=True)
        sqlite_file = os.path.join(db_dir, 'zomato.db')
        conn = sqlite3.connect(sqlite_file)
        init_sqlite_db(conn)
        return conn, 'sqlite'

@app.route('/')
def home():
    """Render the modernized Zomato clone homepage."""
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "zomato-clone"})

@app.route('/api/items', methods=['GET'])
def get_items():
    """Return all available menu items with prices and rich metadata."""
    conn = None
    cursor = None
    try:
        conn, db_type = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id, item_name, price, category_id FROM items")
        rows = cursor.fetchall()

        items = []
        for row in rows:
            item_id = row[0]
            name = row[1]
            price = float(row[2])
            meta = ITEM_METADATA.get(name, {
                'category': 'Specials',
                'is_veg': True,
                'rating': 4.5,
                'rating_count': 100,
                'prep_time': '20-25 min',
                'description': 'Delicious traditional dish prepared fresh with hand-picked spices.',
                'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=700&q=80',
                'badge': 'Popular'
            })
            items.append({
                'item_id': item_id,
                'name': name,
                'price': price,
                'category': meta['category'],
                'is_veg': meta['is_veg'],
                'rating': meta['rating'],
                'rating_count': meta['rating_count'],
                'prep_time': meta['prep_time'],
                'description': meta['description'],
                'image': meta['image'],
                'badge': meta['badge']
            })

        return jsonify({"items": items, "db_engine": db_type}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/place_order', methods=['POST'])
def place_order():
    """Accept and store customer orders."""
    conn = None
    cursor = None
    try:
        order_data = request.get_json(force=True, silent=True)
        if not order_data:
            # Fallback to form data
            cart = []
            biriyani = request.form.get('biriyani_quantity', 0)
            paneer = request.form.get('paneer_quantity', 0)
            butter_chicken = request.form.get('butter_chicken_quantity', 0)
            if int(biriyani or 0) > 0:
                cart.append({'name': 'Biriyani', 'quantity': int(biriyani)})
            if int(paneer or 0) > 0:
                cart.append({'name': 'Paneer', 'quantity': int(paneer)})
            if int(butter_chicken or 0) > 0:
                cart.append({'name': 'Butter Chicken', 'quantity': int(butter_chicken)})
            address = request.form.get('address')
        else:
            cart = order_data.get('cart', [])
            address = order_data.get('address', '').strip()

        if not cart or not address:
            return jsonify({"error": "Cart is empty or delivery address is missing."}), 400

        conn, db_type = create_connection()
        cursor = conn.cursor()

        inserted_ids = []
        user_id = 1

        for item in cart:
            item_name = item.get('name')
            quantity = int(item.get('quantity', 1))

            if quantity <= 0:
                continue

            # Query item
            if db_type == 'mysql':
                cursor.execute("SELECT item_id, price FROM items WHERE item_name = %s", (item_name,))
            else:
                cursor.execute("SELECT item_id, price FROM items WHERE item_name = ?", (item_name,))

            result = cursor.fetchone()
            if not result:
                # Dynamically create item if missing
                if db_type == 'mysql':
                    cursor.execute("INSERT INTO items (item_name, price, category_id) VALUES (%s, %s, %s)", (item_name, 150.00, 1))
                else:
                    cursor.execute("INSERT INTO items (item_name, price, category_id) VALUES (?, ?, ?)", (item_name, 150.00, 1))
                item_id = cursor.lastrowid
            else:
                item_id = result[0]

            # Insert order
            if db_type == 'mysql':
                sql = "INSERT INTO orders (user_id, item_id, quantity, delivery_address) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (user_id, item_id, quantity, address))
            else:
                sql = "INSERT INTO orders (user_id, item_id, quantity, delivery_address) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (user_id, item_id, quantity, address))

            inserted_ids.append(cursor.lastrowid)

        conn.commit()
        return jsonify({
            "message": "Order placed successfully!",
            "order_ids": inserted_ids,
            "address": address,
            "status": "Confirmed"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/orders', methods=['GET'])
def get_orders():
    """Retrieve all placed orders with item details."""
    conn = None
    cursor = None
    try:
        conn, db_type = create_connection()
        cursor = conn.cursor()

        query = """
            SELECT o.order_id, o.user_id, o.quantity, o.delivery_address, o.order_date, i.item_name, i.price
            FROM orders o
            LEFT JOIN items i ON o.item_id = i.item_id
            ORDER BY o.order_id DESC
            LIMIT 50
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        orders = []
        for r in rows:
            orders.append({
                "order_id": r[0],
                "user_id": r[1],
                "quantity": r[2],
                "delivery_address": r[3],
                "order_date": str(r[4]),
                "item_name": r[5] or "Special Item",
                "price": float(r[6]) if r[6] is not None else 0.0,
                "status": "Confirmed"
            })

        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    # Local run on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)