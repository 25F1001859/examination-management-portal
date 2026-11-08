from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    from app.routes import main
    app.register_blueprint(main)
    return app
