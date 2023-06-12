import pytest
from beflask import app as application
from flask_login import FlaskLoginClient
from beflask.models import Benchmark, User, db


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(
        self, username="guest", password="patata", follow_redirects=False
    ):
        return self._client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=follow_redirects,
        )

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app():
    socketio, app = application.create_app("testing")
    app.test_client_class = FlaskLoginClient
    with app.app_context():
        db_seed(db)
    return socketio, app


@pytest.fixture
def client(app):
    return app[1].test_client()


@pytest.fixture
def runner(app):
    return app[1].test_cli_runner()


def db_seed(db):
    db.drop_all()
    db.create_all()
    b = Benchmark(
        name="discretizbench",
        folder="/Users/rmontanana/Code/discretizbench",
        description="Experiments with local discretization and Bayesian "
        "classifiers",
    )
    db.session.add(b)
    b = Benchmark(
        name="odtebench",
        folder="/Users/rmontanana/Code/odtebench",
        description="Experiments with STree and Ensemble classifiers",
    )
    db.session.add(b)
    b = Benchmark(
        name="covbench",
        folder="/Users/rmontanana/Code/covbench",
        description="Experiments with COVID-19 dataset",
    )
    db.session.add(b)
    u = User(
        username="rmontanana",
        email="rmontanana@gmail.com",
        admin=True,
        benchmark_id=1,
    )
    u.set_password("patito")
    u1 = User(
        username="guest",
        email="guest@example.com",
        admin=False,
        benchmark_id=1,
    )
    u1.set_password("patata")
    db.session.add(b)
    db.session.add(u)
    db.session.add(u1)
    db.session.commit()
