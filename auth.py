from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db_connection

auth = Blueprint('auth', __name__)

# Giriş Yap
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')

    return render_template('login.html')

# Yeni Kullanıcı Kaydet
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        key = request.form['key']
        admin_key = "SECRET_ADMIN_KEY"  # Kullanıcıların oluşturulması için gereken anahtar
        if key != admin_key:
            flash('Geçersiz anahtar!', 'error')
            return redirect(url_for('auth.register'))

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Bu kullanıcı adı zaten alınmış!', 'error')
        else:
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Kullanıcı başarıyla oluşturuldu!', 'success')
            return redirect(url_for('auth.login'))

        conn.close()

    return render_template('register.html')

# Çıkış Yap
@auth.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!', 'success')
    return redirect(url_for('auth.login'))
