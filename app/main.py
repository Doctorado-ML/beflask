import os
import dotenv
from benchmark.Utils import Files
from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    redirect,
    request,
    current_app,
)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from .forms import LoginForm
from .models import User, Benchmark, db

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
def index():
    if current_user.is_authenticated:
        if current_user.admin:
            benchmarks = Benchmark.query.all()
        else:
            benchmarks = [current_user.benchmark]
        for benchmark in benchmarks:
            os.chdir(benchmark.folder)
            benchmark.num_files = len(Files.get_all_results(hidden=False))
        os.chdir(current_user.benchmark.folder)
    else:
        benchmarks = []
    return render_template("index.html", benchmarks=benchmarks)


@main.route("/set_benchmark/<benchmark_id>")
@login_required
def set_benchmark(benchmark_id):
    if int(benchmark_id) == current_user.benchmark_id:
        flash("Benchmark already selected.")
        return redirect(url_for(current_app.config["INDEX"]))
    if current_user.admin:
        benchmark = Benchmark.query.filter_by(id=benchmark_id).first()
        if benchmark is None:
            flash("Benchmark not found.", "danger")
            return redirect(url_for(current_app.config["INDEX"]))
        current_user.benchmark = benchmark
        db.session.commit()
    else:
        flash("You are not an admin.", "danger")
    return redirect(url_for(current_app.config["INDEX"]))


@main.route("/config")
@login_required
def config():
    os.chdir(current_user.benchmark.folder)
    env = dotenv.dotenv_values(".env")
    return render_template("config.html", config_env=env)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(current_app.config["INDEX"]))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("main.login"))
        login_user(user, remember=form.remember_me.data)
        user.last_login = db.func.now()
        db.session.commit()
        flash("Logged in successfully.")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for(current_app.config["INDEX"])
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@main.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for(current_app.config["INDEX"]))
