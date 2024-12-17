import pytest
from app import create_app
from app.db import db


@pytest.fixture
def app():
    app = create_app('sqlite:///:memory:')
    app.config.update({
        'TESTING': True,
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
