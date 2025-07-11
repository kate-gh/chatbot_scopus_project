from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

#  Page de connexion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            }
            flash(f" Bonjour {user['name']} !", "success")
            return redirect(url_for('main.index_route'))
        else:
            flash(" Email ou mot de passe incorrect", "danger")

    return render_template('login.html')

#  Page d'inscription
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Vérifie si l'email existe déjà
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash(" Cet email est déjà utilisé. Veuillez en choisir un autre.", "warning")
            cursor.close()
            conn.close()
            return render_template('register.html')

        # Hachage du mot de passe
        hashed_password = generate_password_hash(password)

        # Insertion dans la base
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(" Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

#  Déconnexion
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash(" Vous êtes maintenant déconnecté.", "info")
    return redirect(url_for('auth.login'))
