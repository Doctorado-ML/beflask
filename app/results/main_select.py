import json
import os
import shutil

import xlsxwriter
from benchmark.Datasets import Datasets
from benchmark.ResultsBase import StubReport
from benchmark.ResultsFiles import Excel, ReportDatasets
from benchmark.Utils import Files, Folders
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required

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
def select():
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
    return render_template(
        "select.html",
        files=files,
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
            message=f"This best results file ({file_name}) has not been "
            "created yet! or...",
            error=str(e),
        )
    info = file_name.split("_")
    model = info[3].split(".")[0]
    title = f"Best results obtained with {model} on {info[2]}"
    return render_template("best.html", data=data, title=title)


@results.route("/set_compare", methods=["POST"])
def set_compare():
    compare = request.json["compare"]
    current_app.config.update(COMPARE=compare)
    return AjaxResponse(True, "Ok").to_string()


@results.route("/report/<file_name>")
@login_required
def report(file_name):
    os.chdir(current_user.benchmark.folder)
    back = request.args.get("url") or ""
    with open(os.path.join(Folders.results, file_name)) as f:
        data = json.load(f)
    try:
        summary = process_data(file_name, current_app.config["COMPARE"], data)
    except Exception as e:
        return render_template("error.html", message=str(e))
    return render_template(
        "report.html", data=data, file=file_name, summary=summary, back=back
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


@results.route("/excel", methods=["post"])
@login_required
def excel():
    os.chdir(current_user.benchmark.folder)
    selected_files = request.json["selectedFiles"]
    if selected_files[0] == "datasets":
        # Create a list of datasets
        report = ReportDatasets(excel=True, output=False)
        report.report()
        return AjaxResponse(True, Files.datasets_report_excel).to_string()
    try:
        # create a spreadsheet with the selected files
        book = None
        for file_name in selected_files:
            file_name_result = os.path.join(Folders.results, file_name)
            if book is None:
                file_excel = os.path.join(Folders.excel, Files.be_list_excel)
                book = xlsxwriter.Workbook(
                    file_excel, {"nan_inf_to_errors": True}
                )
            excel = Excel(
                file_name=file_name_result,
                book=book,
                compare=current_app.config["COMPARE"],
            )
            excel.report()
    except Exception as e:
        if book is not None:
            book.close()
        return AjaxResponse(
            False, "Could not create excel file, " + str(e)
        ).to_string()
    if book is not None:
        book.close()
    return AjaxResponse(True, Files.be_list_excel).to_string()


@results.route("/download/<file_name>")
@login_required
def download(file_name):
    os.chdir(current_user.benchmark.folder)
    src = os.path.join(current_user.benchmark.folder, Folders.excel, file_name)
    dest = os.path.join("static", "excel", file_name)
    os.chdir(current_app.root_path)
    shutil.copyfile(src, dest)
    return send_file(dest, as_attachment=True)
