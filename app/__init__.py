from flask import Flask
from app.db import db
from app.routes import website_bp, api_bp


def create_app(database_uri):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    db.init_app(app)

    app.register_blueprint(website_bp)
    app.register_blueprint(api_bp)

    return app
