import os
import dotenv
from benchmark.Utils import Files
from flask import (
    Blueprint,
    render_template,
    current_app,
    url_for,
    flash,
    redirect,
    request,
)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from .forms import LoginForm, UserForm
from .models import User, Benchmark, db

main = Blueprint("main", __name__)

INDEX = "main.index"


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
        return redirect(url_for(INDEX))
    if current_user.admin:
        benchmark = Benchmark.query.filter_by(id=benchmark_id).first()
        if benchmark is None:
            flash("Benchmark not found.", "danger")
            return redirect(url_for(INDEX))
        current_user.benchmark = benchmark
        db.session.commit()
    else:
        flash("You are not an admin.", "danger")
    return redirect(url_for(INDEX))


@main.route("/config")
@login_required
def config():
    os.chdir(current_user.benchmark.folder)
    env = dotenv.dotenv_values(".env")
    return render_template("config.html", config_env=env)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(INDEX))
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
            next_page = url_for(INDEX)
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@main.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for(INDEX))


@main.route("/users")
@login_required
def users():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(INDEX))
    users = User.query.all()
    return render_template("users.html", users=users)


@main.route("/user_edit/<user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    if user_id != current_user.id and not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(INDEX))
    form = UserForm(obj=User.query.filter_by(id=user_id).first())
    form.benchmark_id.choices = [
        (b.id, b.name) for b in Benchmark.query.order_by("name")
    ]
    del form.password
    del form.password2
    form.user_id = user_id
    form.submit.label.text = "Edit User"
    if form.validate_on_submit():
        form.populate_obj(User.query.filter_by(id=user_id).first())
        db.session.commit()
        flash("User edited successfully.")
        return redirect(url_for("main.users"))
    return render_template(
        "user.html",
        form=form,
        alert_type="primary",
        title="Edit User",
    )


@main.route("/user_delete/<user_id>", methods=["GET", "POST"])
@login_required
def user_delete(user_id):
    if user_id != current_user.id and not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(INDEX))
    user = User.query.filter_by(id=user_id).first()
    form = UserForm(obj=user)
    del form.password
    del form.password2
    for field in form:
        if field.type != "SubmitField" and field.type != "CSRFTokenField":
            if field.type == "SelectField" or field.type == "BooleanField":
                field.render_kw = {"disabled": True}
            else:
                field.render_kw = {"readonly": True}

    form.benchmark_id.choices = [
        (b.id, b.name) for b in Benchmark.query.order_by("name")
    ]
    form.submit.label.text = "Delete User"
    form.user_id = user_id
    if form.validate_on_submit():
        flash("User deleted successfully.")
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("main.users"))
    return render_template(
        "user.html",
        form=form,
        alert_type="danger",
        title="Delete User",
    )


@main.route("/user_new", methods=["GET", "POST"])
@login_required
def user_new():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(INDEX))
    form = UserForm()
    user = User()
    form.user_id = None
    form.benchmark_id.choices = [
        (b.id, b.name) for b in Benchmark.query.order_by("name")
    ]
    form.submit.label.text = "New User"
    if form.validate_on_submit():
        form.populate_obj(user)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("User created successfully.")
        return redirect(url_for("main.users"))
    return render_template(
        "user.html", form=form, alert_type="info", title="New User"
    )
