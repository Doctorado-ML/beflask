import os
import json
from benchmark.Utils import Files, Folders
from benchmark.ResultsBase import StubReport
from benchmark.Datasets import Datasets
from flask_login import current_user
from flask import Blueprint, current_app, send_file
from flask import render_template, current_app, request, redirect, url_for
from flask_login import login_required

# import shutil
# import xlsxwriter
# from benchmark.ResultsFiles import Excel, ReportDatasets

results = Blueprint("results", __name__, template_folder="templates")


class AjaxResponse:
    def __init__(self, success, file_name, code=200):
        self.success = success
        self.file_name = file_name
        self.code = code

    def to_string(self):
        return (
            json.dumps(
                {
                    "success": self.success,
                    "file": self.file_name,
                }
            ),
            self.code,
            {"ContentType": "application/json"},
        )


@results.route("/select")
@login_required
def select(compare="False"):
    # Get a list of files in a directory
    files = {}
    os.chdir(current_user.benchmark.folder)
    names = Files.get_all_results(hidden=False)
    for name in names:
        report = StubReport(os.path.join(Folders.results, name))
        report.report()
        files[name] = {
            "duration": report.duration,
            "score": report.score,
            "title": report.title,
        }
    candidate = current_app.config["FRAMEWORKS"].copy()
    candidate.remove(current_app.config["FRAMEWORK"])
    return render_template(
        "select.html",
        files=files,
        candidate=candidate[0],
        framework=current_app.config["FRAMEWORK"],
        compare=compare.capitalize() == "True",
    )


@results.route("/datasets")
@login_required
def datasets():
    os.chdir(current_user.benchmark.folder)
    dt = Datasets()
    datos = []
    for dataset in dt:
        datos.append(dt.get_attributes(dataset))
    return render_template("datasets.html", datasets=datos)


@results.route("/best/<file_name>")
@login_required
def best(file_name):
    os.chdir(current_user.benchmark.folder)
    try:
        with open(os.path.join(Folders.results, file_name)) as f:
            data = json.load(f)
    except Exception as e:
        return render_template(
            "error.html",
            message=f"This best results file ({file_name}) has not been created yet!",
        )
    return render_template("best.html", data=data)


@results.route("/set_compare", methods=["POST"])
def set_compare():
    compare = request.json["compare"]
    current_app.config.update(COMPARE=compare)
    return AjaxResponse(True, "Ok").to_string()


@results.route("/report/<file_name>")
@login_required
def report(file_name):
    os.chdir(current_user.benchmark.folder)
    with open(os.path.join(Folders.results, file_name)) as f:
        data = json.load(f)
    try:
        summary = process_data(file_name, current_app.config["COMPARE"], data)
    except Exception as e:
        return render_template("error.html", message=str(e))
    return render_template(
        "report.html",
        data=data,
        file=file_name,
        summary=summary,
    )


def process_data(file_name, compare, data):
    report = StubReport(
        os.path.join(Folders.results, file_name), compare=compare
    )
    new_list = []
    for result in data["results"]:
        symbol = report._compute_status(result["dataset"], result["score"])
        result["symbol"] = symbol if symbol != " " else "&nbsp;"
        new_list.append(result)
    data["results"] = new_list
    # Compute summary with explanation of symbols
    summary = {}
    for key, value in report._compare_totals.items():
        summary[key] = (report._status_meaning(key), value)
    return summary
