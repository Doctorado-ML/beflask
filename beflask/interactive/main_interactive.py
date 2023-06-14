import os
import json
import shutil
from pathlib import Path

import dotenv
from benchmark.Datasets import Datasets
from benchmark.Experiments import Experiment
from benchmark.Models import Models
from benchmark.ResultsFiles import Benchmark
from benchmark.Utils import Folders
from flask import Blueprint, current_app, render_template, url_for
from flask_login import current_user, login_required

from .forms import BenchmarkDatasetForm
from ..results.main_results import prepare_report

interactive = Blueprint("interactive", __name__, template_folder="templates")


@interactive.route("/ranking")
@login_required
def ranking():
    os.chdir(current_user.benchmark.folder)
    return render_template("ranking.html")


@interactive.route("/experiment", methods=["GET", "POST"])
@login_required
def experiment():
    os.chdir(current_user.benchmark.folder)
    env = dotenv.dotenv_values(".env")
    models = Models.define_models(random_state=0).keys()
    form = BenchmarkDatasetForm()
    form.dataset.choices = [(d, d) for d in list(Datasets())]
    form.model.choices = [(b, b) for b in models]
    if form.validate_on_submit():
        model = form.model.data
        score = form.score.data
        dataset = form.dataset.data
        n_folds = form.n_folds.data
        stratified = "1" if form.stratified.data else "0"
        discretize = "1" if form.discretize.data else "0"
        ignore_nan = "1" if form.ignore_nan.data else "0"
        fit_features = "1" if form.fit_features.data else "0"
        hyperparameters = form.hyperparameters.data or "{}"
        back = url_for("interactive.experiment")
        try:
            json.loads(hyperparameters)
        except json.JSONDecodeError as e:
            return render_template(
                "error.html",
                message="Hyperparameters has to be a valid JSON",
                error=str(e),
                back=back,
            )
        try:
            job = Experiment(
                score_name=score,
                model_name=model,
                stratified=stratified,
                datasets=Datasets(dataset_name=dataset, discretize=discretize),
                hyperparams_dict=hyperparameters,
                hyperparams_file=None,
                grid_paramfile=None,
                progress_bar=False,
                platform="BeFlask",
                ignore_nan=ignore_nan,
                title="Created by the web interface",
                folds=n_folds,
                fit_features=fit_features,
                discretize=discretize,
            )
            job.do_experiment()
        except ValueError as e:
            breakpoint()
            return render_template(
                "error.html",
                message=f"Couldn't complete the experiment!!",
                error=str(e),
                back=back,
            )
        else:
            file_name = str(Path(job.get_output_file()).name)
            try:
                result = prepare_report(file_name)
            except FileNotFoundError as e:
                return render_template(
                    "error.html",
                    message=f"This results file ({file_name}) "
                    "has not been found!",
                    error=str(e),
                    back=back,
                )
            except ValueError as e:
                return render_template(
                    "error.html",
                    message=str(e),
                    back=url_for("results.select"),
                )
            os.remove(os.path.join(Folders.results, file_name))
            return render_template(
                "report.html",
                data=result["data"],
                file=file_name,
                summary=result["summary"],
                back=back,
                back_name="Experiment",
                app_config=result["app_config"],
                excel=False,
            )

    form.model.data = env.get("model")
    form.score.data = env.get("score")
    form.n_folds.data = env.get("n_folds", 5)
    form.stratified.data = env.get("stratified", "0") == "1"
    form.discretize.data = env.get("discretize", "0") == "1"
    return render_template("experiment.html", form=form, title="Experiment")


@current_app.socket.on("client")
def handle_client(message):
    current_app.logger.info(message)
    match message.get("action"):
        case "ReadyToRock!":
            # Benchmark
            get_benchmark(
                score=message.get("score"),
                excel=message.get("excel", False),
                html=message.get("html", False),
            )
        case "ReadyToRoll!":
            # Experiment
            pass
    current_app.socket.emit("server", {"message": "Ready!", "percentage": 0})


def send_message(message, percentage, status="Ok", payload={}):
    output = {
        "message": message,
        "percentage": percentage,
        "status": status,
        "payload": payload,
    }
    current_app.socket.emit("server", output)


def get_benchmark(score, excel=False, html=False):
    def move_exreport():
        src = os.path.join(
            current_user.benchmark.folder, "exreport", "exreport_output"
        )
        dst = os.path.join(
            current_app.static_folder, "exreport", "exreport_output"
        )
        shutil.copytree(src, dst, dirs_exist_ok=True)

    def progress(step):
        values = [0, 40, 60, 80]
        if excel:
            values = [0, 20, 40, 60, 80, 100]
        return values[step]

    benchmark = Benchmark(score=score, visualize=html)
    send_message("Start", 0)
    try:
        send_message("Generating ranking...", 0)
        benchmark.compile_results()
        send_message("Saving results...", progress(1))
        benchmark.save_results()
        send_message("Generating report...", progress(2))
        benchmark.report(tex_output=False)
        send_message("Generating exreport...", progress(3))
        benchmark.exreport()
        if excel:
            send_message("Generating excel...", progress(4))
            benchmark.excel()
    except ValueError as e:
        send_message(
            "Error: Couldn't generate ranking. " + str(e),
            percentage=100,
            status="Error",
        )
        return
    except KeyError as e:
        send_message(
            "Couldn't generate ranking. It seems that there are "
            "partial results for some classifierss. "
            f"Key not found {str(e)}",
            percentage=100,
            status="Error",
        )
        return
    # copy the results to the static folder
    if html:
        move_exreport()
    excel_payload = (
        ""
        if not excel
        else url_for(
            "results.download",
            file_name=str(Path(benchmark.get_excel_file_name()).name),
        )
    )
    html_payload = (
        ""
        if not html
        else url_for("static", filename="exreport/exreport_output/report.html")
    )
    current_app.logger.info("excel_payload:" + excel_payload)
    send_message(
        "Done!",
        100,
        payload={
            "excel": excel_payload,
            "html": html_payload,
        },
    )
