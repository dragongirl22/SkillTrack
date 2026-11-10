from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from modules.csv_handler import parse_students, validate_students
from modules.tracker import verify_students, build_demo_results
import csv, io, json, os

app = Flask(__name__)
app.secret_key = os.environ.get("SKILLTRACK_SECRET", "local-development-key")
REQUIRED = 10

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    mode = request.form.get("mode", "live")
    delay = request.form.get("delay", "3")
    retries = request.form.get("retries", "2")
    if request.method == "POST":
        try:
            upload = request.files.get("csv_file")
            if upload and upload.filename:
                students = parse_students(io.StringIO(upload.stream.read().decode("utf-8-sig")))
            elif request.form.get("use_sample"):
                with open("data/GDG_Tech_Lead_Task_Sample.csv", encoding="utf-8-sig", newline="") as f:
                    students = parse_students(f)
            else:
                flash("Upload a CSV or select the sample file.", "error")
                return redirect(url_for("index"))
            students, issues = validate_students(students)
            for issue in issues:
                flash(issue, "warning")
            if mode == "demo":
                results = build_demo_results(students, REQUIRED)
            else:
                results = verify_students(students, REQUIRED, max(1,min(30,int(delay))), max(0,min(4,int(retries))))
        except Exception as exc:
            flash(f"Could not process CSV: {exc}", "error")
    return render_template("index.html", results=results, mode=mode, delay=delay, retries=retries, required=REQUIRED)

@app.post("/download")
def download():
    try:
        rows = json.loads(request.form.get("results_json", "[]"))
        out = io.StringIO()
        fields = ["Student","Profile name","Email","Profile URL","Badges","Progress","Status","Reference note","Checked","Details"]
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        response = make_response(out.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=skilltrack_results.csv"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        return response
    except Exception as exc:
        flash(f"Export failed: {exc}", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
