from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskr.config import BaseConfig, DevConfig

login_manager = LoginManager()
login_manager.login_view = 'app.index'
login_manager.login_message = 'ログインしてください。'

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)
    from flaskr.views import bp
    app.register_blueprint(bp)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app