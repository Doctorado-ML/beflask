import os
import shutil
from pathlib import Path
from flask import Blueprint, render_template, url_for, current_app
from benchmark.ResultsFiles import Benchmark
from flask_login import current_user, login_required

interactive = Blueprint("interactive", __name__, template_folder="templates")


@interactive.route("/ranking")
@login_required
def ranking():
    os.chdir(current_user.benchmark.folder)
    return render_template("ranking.html")


@current_app.socket.on("client")
def handle_client(message):
    current_app.logger.info(message)
    if message.get("action") == "ReadyToRock!":
        get_benchmark(message.get("score"), excel=message.get("excel", False))
    current_app.socket.emit("server", {"message": "Ready!", "percentage": 0})


def send_message(message, percentage, status="Ok", payload={}):
    output = {
        "message": message,
        "percentage": percentage,
        "status": status,
        "payload": payload,
    }
    current_app.socket.emit("server", output)


def get_benchmark(score, excel=False):
    def move_exreport():
        src = os.path.join(
            current_user.benchmark.folder, "exreport", "exreport_output"
        )
        dst = os.path.join(
            current_app.static_folder, "exreport", "exreport_output"
        )
        shutil.copytree(src, dst, dirs_exist_ok=True)

    benchmark = Benchmark(score=score, visualize=True)
    send_message("Start", 0)
    try:
        send_message("Generating ranking...", 0)
        benchmark.compile_results()
        send_message("Saving results...", 20 if excel else 40)
        benchmark.save_results()
        send_message("Generating report...", 40 if excel else 60)
        benchmark.report(tex_output=False)
        send_message("Generating exreport...", 60 if excel else 80)
        benchmark.exreport()
        if excel:
            send_message("Generating excel...", 80)
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
    move_exreport()
    excel_payload = (
        "" if not excel else str(Path(benchmark.get_excel_file_name()))
    )
    current_app.logger.info("excel_payload:" + excel_payload)
    send_message(
        "Done!",
        100,
        payload={
            "excel": excel_payload,
            "html": url_for(
                "static", filename="exreport/exreport_output/report.html"
            ),
        },
    )
