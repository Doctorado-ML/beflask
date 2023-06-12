import pytest
from beflask import app as application
from flask_login import FlaskLoginClient
from beflask.models import Benchmark, User, db


class AuthActions(object):
    guest_user = "guest"
    guest_password = "patata"

    def __init__(self, client):
        self._client = client

    def login(
        self,
        username=None,
        password=None,
        follow_redirects=False,
    ):
        username = username or self.guest_user
        password = password or self.guest_password
        return self._client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=follow_redirects,
        )

    def logout(self, follow_redirects=False):
        return self._client.get("/logout", follow_redirects=follow_redirects)


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app(admin_user, admin_password):
    socketio, app = application.create_app("testing")
    app.test_client_class = FlaskLoginClient
    with app.app_context():
        db_seed(db, admin_user, admin_password)
    return socketio, app


@pytest.fixture
def client(app):
    return app[1].test_client()


@pytest.fixture
def runner(app):
    return app[1].test_cli_runner()


@pytest.fixture
def admin_user():
    return "rmontanana"


@pytest.fixture
def admin_password():
    return "patito"


@pytest.fixture
def guest_user():
    return AuthActions.guest_user


@pytest.fixture
def guest_password():
    return AuthActions.guest_password


def db_seed(db, admin_user, admin_password):
    db.drop_all()
    db.create_all()
    b = Benchmark(
        name="discretizbench",
        folder="/Users/rmontanana/Code/discretizbench",
        description="Experiments with local discretization and Bayesian"
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
        username=admin_user,
        email="rmontanana@gmail.com",
        admin=True,
        benchmark_id=1,
    )
    u.set_password(admin_password)
    u1 = User(
        username=AuthActions.guest_user,
        email="guest@example.com",
        admin=False,
        benchmark_id=1,
    )
    u1.set_password(AuthActions.guest_password)
    db.session.add(b)
    db.session.add(u)
    db.session.add(u1)
    db.session.commit()
