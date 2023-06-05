from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    redirect,
    request,
)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from .forms import LoginForm
from .models import User, Benchmark

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
def index():
    if current_user.is_authenticated:
        if current_user.admin:
            benchmarks = Benchmark.query.all()
        else:
            benchmarks = [current_user.benchmark]
    else:
        benchmarks = []
    return render_template("index.html", benchmarks=benchmarks)


@main.route("/config")
@login_required
def config():
    return render_template("config.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))
        login_user(user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
