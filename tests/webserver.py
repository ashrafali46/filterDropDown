"""
webserver for testing filterDropDown

Shows a website with all test scenarios
and implents API for AJAX calls: regular and server side processing
"""

import json
from operator import itemgetter
from pathlib import Path
import re

from flask import Flask, render_template, Blueprint, jsonify, request

app = Flask(__name__)
static_path = Path(__file__).parent.parent / "js"
blueprint = Blueprint(
    "site", __name__, static_url_path="/static/site", static_folder=str(static_path)
)
app.register_blueprint(blueprint)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Welcome")


@app.route("/test_vanilla", methods=["GET"])
def vanilla():
    return render_template("test.html", title="Test Vanilla")


@app.route("/test_bootstrap", methods=["GET"])
def bootstrap():
    return render_template("test_bs.html", title="Test Bootstrap")


@app.route("/test_server_side", methods=["GET"])
def server_side():
    return render_template("test_server_side.html", title="Test Server Side")


@app.route("/data", methods=["GET"])
def data():
    """API for regular AJAX calls"""
    filepath = Path(__file__).parent / "data.json"
    with filepath.open("r") as f:
        data = json.load(f)

    return jsonify(data)


@app.route("/data_server_side", methods=["GET"])
def data_server_side():
    """API for AJAX calls for server side processing"""
    filepath = Path(__file__).parent / "data_2.json"
    with filepath.open("r") as f:
        data_raw = json.load(f)["data"]

    # collect column info
    columns = dict()
    num = 0
    while True:
        if request.args.get(f"columns[{num}][data]"):
            columns[num] = dict()
            columns[num]["data"] = request.args.get(f"columns[{num}][data]")
            columns[num]["search_value"] = request.args.get(
                f"columns[{num}][search][value]"
            )
            columns[num]["search_regex"] = (
                request.args.get(f"columns[{num}][search][regex]") == "true"
            )
            num += 1
        else:
            break

    # global search
    global_search = request.args.get("search[value]")
    if global_search:
        data = [
            row for row in data_raw if global_search in "".join(row.values()).lower()
        ]
    else:
        data = data_raw

    # columns search
    for num in columns:
        if columns[num]["search_value"] and columns[num]["search_regex"]:
            data = [
                row
                for row in data
                if re.search(
                    columns[num]["search_value"], row.get(columns[num]["data"])
                )
            ]

    # order
    order_column_num = int(request.args.get("order[0][column]"))
    order_dir = request.args.get("order[0][dir]")
    if order_dir == "desc":
        data = sorted(
            data, key=itemgetter(columns[order_column_num]["data"]), reverse=True
        )
    else:
        data = sorted(data, key=itemgetter(columns[order_column_num]["data"]))

    # build response page
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    response = {
        "draw": request.args.get("draw"),
        "data": data[start : start + length],
        "recordsTotal": len(data),
        "recordsFiltered": len(data),
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000