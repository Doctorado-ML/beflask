#!/usr/bin/env python
# import os
# import json
# import shutil
# import xlsxwriter
# from benchmark.Utils import Files, Folders
# from benchmark.Arguments import EnvData
# from benchmark.ResultsBase import StubReport
# from benchmark.ResultsFiles import Excel, ReportDatasets
# from benchmark.Datasets import Datasets
# from flask import Blueprint, current_app, send_file
# from flask import render_template, request, redirect, url_for
from flask import Blueprint, render_template


results = Blueprint("results", __name__, template_folder="results")
# FRAMEWORK = "framework"
# FRAMEWORKS = "frameworks"
# OUTPUT = "output"
# TEST = "test"


# class AjaxResponse:
#     def __init__(self, success, file_name, code=200):
#         self.success = success
#         self.file_name = file_name
#         self.code = code

#     def to_string(self):
#         return (
#             json.dumps(
#                 {
#                     "success": self.success,
#                     "file": self.file_name,
#                     "output": current_app.config[OUTPUT],
#                 }
#             ),
#             self.code,
#             {"ContentType": "application/json"},
#         )


# def process_data(file_name, compare, data):
#     report = StubReport(
#         os.path.join(Folders.results, file_name), compare=compare
#     )
#     new_list = []
#     for result in data["results"]:
#         symbol = report._compute_status(result["dataset"], result["score"])
#         result["symbol"] = symbol if symbol != " " else "&nbsp;"
#         new_list.append(result)
#     data["results"] = new_list
#     # Compute summary with explanation of symbols
#     summary = {}
#     for key, value in report._compare_totals.items():
#         summary[key] = (report._status_meaning(key), value)
#     return summary


@results.route("/results/<compare>")
def results(compare="False"):
    # # Get a list of files in a directory
    # files = {}
    # names = Files.get_all_results(hidden=False)
    # for name in names:
    #     report = StubReport(os.path.join(Folders.results, name))
    #     report.report()
    #     files[name] = {
    #         "duration": report.duration,
    #         "score": report.score,
    #         "title": report.title,
    #     }
    # candidate = current_app.config[FRAMEWORKS].copy()
    # candidate.remove(current_app.config[FRAMEWORK])
    # return render_template(
    #     "select.html",
    #     files=files,
    #     candidate=candidate[0],
    #     framework=current_app.config[FRAMEWORK],
    #     compare=compare.capitalize() == "True",
    # )
    return render_template("test.html")


""" 
@results.route("/datasets/<compare>")
@results.route("datasets")
def datasets(compare=False):
    dt = Datasets()
    datos = []
    for dataset in dt:
        datos.append(dt.get_attributes(dataset))
    return render_template(
        "datasets.html",
        datasets=datos,
        compare=compare,
        framework=current_app.config[FRAMEWORK],
    )


@results.route("/showfile/<file_name>/<compare>")
def showfile(file_name, compare, back=None):
    compare = compare.capitalize() == "True"
    back = request.args["url"] if back is None else back
    print(f"back [{back}]")
    with open(os.path.join(Folders.results, file_name)) as f:
        data = json.load(f)
    try:
        summary = process_data(file_name, compare, data)
    except Exception as e:
        return render_template("error.html", message=str(e), compare=compare)
    return render_template(
        "report.html",
        data=data,
        file=file_name,
        summary=summary,
        framework=current_app.config[FRAMEWORK],
        back=back,
    )


@results.route("/show", methods=["post"])
def show():
    selected_file = request.form["selected-file"]
    compare = request.form["compare"]
    return showfile(
        file_name=selected_file,
        compare=compare,
        back=url_for(
            "main.index", compare=compare, output=current_app.config[OUTPUT]
        ),
    )


@results.route("/excel", methods=["post"])
def excel():
    selected_files = request.json["selectedFiles"]
    compare = request.json["compare"]
    book = None
    if selected_files[0] == "datasets":
        # Create a list of datasets
        report = ReportDatasets(excel=True, output=False)
        report.report()
        excel_name = os.path.join(Folders.excel, Files.datasets_report_excel)
        if current_app.config[OUTPUT] == "local":
            Files.open(excel_name, test=current_app.config[TEST])
        return AjaxResponse(True, Files.datasets_report_excel).to_string()
    try:
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
                compare=compare,
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
    if current_app.config[OUTPUT] == "local":
        Files.open(file_excel, test=current_app.config[TEST])
    return AjaxResponse(True, Files.be_list_excel).to_string()


@results.route("/download/<file_name>")
def download(file_name):
    src = os.path.join(Folders.current, Folders.excel, file_name)
    dest = os.path.join(
        Folders.src(), "scripts", "app", "static", "excel", file_name
    )
    shutil.copyfile(src, dest)
    return send_file(dest, as_attachment=True)


@results.route("/config/<framework>/<compare>")
def config(framework, compare):
    if framework not in current_app.config[FRAMEWORKS]:
        message = f"framework {framework} not supported"
        return render_template("error.html", message=message)
    env = EnvData()
    env.load()
    env.args[FRAMEWORK] = framework
    env.save()
    current_app.config[FRAMEWORK] = framework
    return redirect(url_for("main.index", compare=compare))


@results.route("/best_results/<file>/<compare>")
def best_results(file, compare):
    compare = compare.capitalize() == "True"
    try:
        with open(os.path.join(Folders.results, file)) as f:
            data = json.load(f)
    except Exception as e:
        return render_template("error.html", message=str(e), compare=compare)
    return render_template(
        "report_best.html",
        data=data,
        compare=compare,
        framework=current_app.config[FRAMEWORK],
    )
 """
