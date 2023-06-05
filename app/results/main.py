import os
from benchmark.Utils import Files, Folders
from benchmark.ResultsBase import StubReport
from flask import Blueprint, current_app, send_file
from flask import render_template, current_app, request, redirect, url_for
from flask_login import login_required

# import json
# import shutil
# import xlsxwriter
# from benchmark.ResultsFiles import Excel, ReportDatasets
# from benchmark.Datasets import Datasets

results = Blueprint("results", __name__, template_folder="templates")


@results.route("/select")
@login_required
def select(compare="False"):
    # Get a list of files in a directory
    files = {}
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
def datasets(compare="False"):
    return render_template("test.html")
