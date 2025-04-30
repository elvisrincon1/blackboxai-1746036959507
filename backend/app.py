from flask import Flask, request, jsonify, session, send_from_directory
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

Session(app)

DATABASE = 'database.sqlite'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price_suggested REAL NOT NULL,
            price_affiliate REAL NOT NULL,
            images TEXT,
            published_by INTEGER,
            published INTEGER DEFAULT 0,
            FOREIGN KEY(published_by) REFERENCES users(id)
        )
    ''')
    conn.commit()
    # Insert default users if not exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        users = [
            ('master', generate_password_hash('master123'), 'master'),
            ('supervisor', generate_password_hash('supervisor123'), 'supervisor'),
            ('afiliado', generate_password_hash('afiliado123'), 'afiliado')
        ]
        cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)
        conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({'message': 'Login successful', 'role': user['role']})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@app.route('/api/me', methods=['GET'])
@login_required
def me():
    return jsonify({
        'id': session['user_id'],
        'username': session['username'],
        'role': session['role']
    })

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    if session.get('role') != 'master':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not username or not password or not role:
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, generate_password_hash(password), role))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'User already exists'}), 409
    conn.close()
    return jsonify({'id': user_id, 'username': username, 'role': role})

@app.route('/api/users', methods=['GET'])
@login_required
def list_users():
    if session.get('role') != 'master':
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if session.get('role') != 'master':
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    if changes == 0:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User deleted'})

@app.route('/api/products', methods=['POST'])
@login_required
def create_product():
    if session.get('role') not in ['master', 'supervisor']:
        return jsonify({'error': 'Forbidden'}), 403
    name = request.form.get('nombre_producto')
    description = request.form.get('descripcion_producto')
    price_suggested = request.form.get('precio_sugerido')
    price_affiliate = request.form.get('precio_afiliado')
    if not all([name, description, price_suggested, price_affiliate]):
        return jsonify({'error': 'Missing fields'}), 400
    try:
        price_suggested = float(price_suggested)
        price_affiliate = float(price_affiliate)
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400
    if price_suggested <= price_affiliate:
        return jsonify({'error': 'Precio sugerido debe ser mayor que precio para afiliado'}), 400
    images = []
    if 'imagenes_producto' in request.files:
        files = request.files.getlist('imagenes_producto')
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            images.append(filename)
    images_str = ','.join(images)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, description, price_suggested, price_affiliate, images, published_by)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, price_suggested, price_affiliate, images_str, session['user_id']))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': product_id, 'name': name, 'description': description, 'price_suggested': price_suggested, 'price_affiliate': price_affiliate, 'images': images_str})

@app.route('/api/products', methods=['GET'])
@login_required
def list_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

@app.route('/api/products/<int:product_id>/publish', methods=['POST'])
@login_required
def publish_product(product_id):
    if session.get('role') != 'afiliado':
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET published = 1 WHERE id = ?', (product_id,))
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    if changes == 0:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product marked as published'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
