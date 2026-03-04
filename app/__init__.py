from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User

    # 🔑 THIS IS THE FIX
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.main.routes import main
    from app.auth.routes import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app
