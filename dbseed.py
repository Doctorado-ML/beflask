from app.models import Benchmark, db, User
from app import app

app = app.create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    b = Benchmark(
        name="discretizbench",
        folder="proyects/discretizbench",
        description="Experiments with local discretization and Bayesian classifiers",
    )
    u = User(username="rmontanana", email="rmontanana@gmail.com", admin=True)
    u.set_password("patata")
    u1 = User(
        username="guest",
        email="guest@example.com",
        admin=False,
        benchmark_id=1,
    )
    u1.set_password("guest")
    db.session.add(b)
    db.session.add(u)
    db.session.add(u1)
    db.session.commit()
