from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import init_db, get_db_connection
from auth import auth  # Kullanıcı giriş işlemleri için auth blueprint
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Blueprint'i ekle
app.register_blueprint(auth, url_prefix='/auth')

# Giriş yapılmasını zorunlu tutan decorator
@app.before_request
def require_login():
    allowed_routes = ['auth.login', 'auth.register', 'static']
    if 'user_id' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('auth.login'))

# Ana Sayfa: Ürünlerin listelendiği sayfa
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Yeni Ürün Ekle
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
        conn.commit()
        conn.close()
        flash('Yeni ürün başarıyla eklendi!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

# Ürün Düzenle
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        conn = get_db_connection()
        conn.execute('UPDATE products SET name = ?, price = ? WHERE id = ?', (name, price, id))
        conn.commit()
        conn.close()
        flash('Ürün başarıyla güncellendi!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)

# Ürün Sil
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Ürün başarıyla silindi!', 'success')
    return redirect(url_for('index'))

# Uygulama çalıştırma
if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()  # Veritabanını oluştur
    app.run(debug=True)
