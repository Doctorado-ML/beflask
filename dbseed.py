from app.models import Benchmark, db, User
from app import app

app = app.create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    b = Benchmark(
        name="discretizbench",
        folder="/Users/rmontanana/Code/discretizbench",
        description="Experiments with local discretization and Bayesian classifiers",
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
