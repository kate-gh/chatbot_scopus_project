from flask import Flask
from app.routes import bp as main_bp
from app.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'my_super_secret'
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Pour /auth/login, /auth/register
    app.register_blueprint(main_bp)  # Chatbot sur /
    return app
