from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    redirect,
    current_app,
)
from flask_login import current_user, login_required
from .forms import UserForm, UpdatePasswordForm, BenchmarkForm
from ..models import User, Benchmark, db

admin = Blueprint("admin", __name__, template_folder="templates")


@admin.route("/users")
@login_required
def users():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    users = User.query.all()
    return render_template("users.html", users=users)


@admin.route("/user_edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    if user_id != current_user.id and not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
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
        return redirect(url_for("admin.users"))
    return render_template(
        "user.html",
        form=form,
        alert_type="primary",
        title="Edit User",
    )


@admin.route("/user_delete/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_delete(user_id):
    if user_id != current_user.id and not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    user = User.query.filter_by(id=user_id).first()
    form = UserForm(obj=user)
    del form.password
    del form.password2
    disable_fields(form)

    form.benchmark_id.choices = [
        (b.id, b.name) for b in Benchmark.query.order_by("name")
    ]
    form.submit.label.text = "Delete User"
    form.user_id = user_id
    if form.validate_on_submit():
        flash("User deleted successfully.")
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("admin.users"))
    return render_template(
        "user.html",
        form=form,
        alert_type="danger",
        title="Delete User",
    )


@admin.route("/user_new", methods=["GET", "POST"])
@login_required
def user_new():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
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
        return redirect(url_for("admin.users"))
    return render_template(
        "user.html", form=form, alert_type="info", title="New User"
    )


@admin.route(
    "/password/<int:user_id>/<back>",
    methods=["GET", "POST"],
)
@admin.route(
    "/password/<int:user_id>",
    defaults={"back": "None"},
    methods=["GET", "POST"],
)
@login_required
def password(user_id, back):
    if not current_user.admin and user_id != current_user.id:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    form = UpdatePasswordForm()
    user = User.query.filter_by(id=user_id).first()
    form.submit.label.text = "Update Password"
    destination = current_app.config["INDEX"] if back == "None" else back
    if form.validate_on_submit():
        form.populate_obj(user)
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated successfully.")
        return redirect(url_for(destination))
    return render_template(
        "password.html", form=form, back=destination, user_name=user.username
    )


@admin.route("/benchmarks")
@login_required
def benchmarks():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    benchmarks = Benchmark.query.all()
    return render_template("benchmarks.html", benchmarks=benchmarks)


@admin.route("/benchmark_edit/<int:benchmark_id>", methods=["GET", "POST"])
@login_required
def benchmark_edit(benchmark_id):
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    form = BenchmarkForm(
        obj=Benchmark.query.filter_by(id=benchmark_id).first()
    )
    form.submit.label.text = "Edit Benchmark"
    if form.validate_on_submit():
        form.populate_obj(Benchmark.query.filter_by(id=benchmark_id).first())
        db.session.commit()
        flash("Benchmark edited successfully.")
        return redirect(url_for("admin.benchmarks"))
    return render_template(
        "benchmark.html",
        form=form,
        alert_type="primary",
        title="Edit Benchmark",
    )


def disable_fields(form):
    for field in form:
        if field.type != "SubmitField" and field.type != "CSRFTokenField":
            if field.type == "SelectField" or field.type == "BooleanField":
                field.render_kw = {"disabled": True}
            else:
                field.render_kw = {"readonly": True}


@admin.route("/benchmark_delete/<int:benchmark_id>", methods=["GET", "POST"])
@login_required
def benchmark_delete(benchmark_id):
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    benchmark = Benchmark.query.filter_by(id=benchmark_id).first()
    form = BenchmarkForm(obj=benchmark)
    disable_fields(form)
    form.submit.label.text = "Delete Benchmark"
    if form.validate_on_submit():
        flash("Benchmark deleted successfully.")
        db.session.delete(benchmark)
        db.session.commit()
        return redirect(url_for("admin.benchmarks"))
    return render_template(
        "benchmark.html",
        form=form,
        alert_type="danger",
        title="Delete Benchmark",
    )


@admin.route("/benchmark_new", methods=["GET", "POST"])
@login_required
def benchmark_new():
    if not current_user.admin:
        flash("You are not an admin.", "danger")
        return redirect(url_for(current_app.config["INDEX"]))
    form = BenchmarkForm()
    benchmark = Benchmark()
    form.submit.label.text = "New Benchmark"
    if form.validate_on_submit():
        form.populate_obj(benchmark)
        db.session.add(benchmark)
        db.session.commit()
        flash("Benchmark created successfully.")
        return redirect(url_for("admin.benchmarks"))
    return render_template(
        "benchmark.html", form=form, alert_type="info", title="New Benchmark"
    )
