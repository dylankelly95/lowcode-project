import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort, flash
import db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))


@app.route("/")
def index():
    portfolio = db.get_first_portfolio()
    projects = db.list_projects()
    featured_work = db.list_media()[:6]
    return render_template(
        "index.html",
        portfolio=portfolio,
        featured_work=featured_work,
        projects=projects,
    )


@app.route("/projects")
def list_projects():
    projects = db.list_projects()
    return render_template("projects.html", projects=projects)


@app.route("/projects/new", methods=["GET"])
def new_project_form():
    return render_template("project_form.html")


@app.route("/projects", methods=["POST"])
def create_project():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category_medium = request.form.get("category_medium", "").strip() or "General"
    release_date = request.form.get("release_date", "").strip() or None

    if not title:
        flash("Project title is required.")
        return render_template("project_form.html", title=title, description=description), 400

    if len(title) > 200:
        flash("Project title must be 200 characters or fewer.")
        return render_template("project_form.html", title=title, description=description), 400

    if not description:
        flash("Project description is required.")
        return render_template("project_form.html", title=title, description=description), 400

    if len(description) > 500:
        flash("Description must be 500 characters or fewer.")
        return render_template("project_form.html", title=title, description=description), 400

    portfolio = db.get_first_portfolio()
    if portfolio is None:
        flash("No portfolio exists yet. Please create a user and portfolio first.")
        return render_template("project_form.html", title=title, description=description), 400

    try:
        db.create_project(
            portfolio_id=portfolio["portfolio_id"],
            title=title,
            description=description,
            category_medium=category_medium,
            release_date=release_date,
        )
    except sqlite3.IntegrityError as err:
        flash(f"Could not save project: {err}")
        return render_template("project_form.html", title=title, description=description), 400

    return redirect(url_for("list_projects"))


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = db.get_project(project_id)
    if project is None:
        abort(404)

    work_items = db.list_media(project_id=project_id)
    return render_template("project_detail.html", project=project, work_items=work_items)


@app.route("/work")
def list_work():
    work_items = db.list_media()
    return render_template("work.html", work_items=work_items)


@app.route("/work/new", methods=["GET"])
def new_work_form():
    projects = db.list_projects()
    return render_template("work_form.html", projects=projects)


@app.route("/work", methods=["POST"])
def create_work():
    file_name = (
        request.form.get("file_name", "").strip()
        or request.form.get("title", "").strip()
    )
    file_type = (
        request.form.get("file_type", "").strip()
        or request.form.get("media_type", "").strip()
    )
    file_url = (
        request.form.get("file_url", "").strip()
        or request.form.get("media_url", "").strip()
    )
    project_id_raw = request.form.get("project_id", "").strip()
    project_id = int(project_id_raw) if project_id_raw.isdigit() else None

    projects = db.list_projects()

    if not file_name:
        flash("Media file name / title is required.")
        return render_template("work_form.html", projects=projects), 400

    if not file_url:
        flash("Media URL is required.")
        return render_template("work_form.html", projects=projects), 400

    if project_id is None:
        flash("Please select a valid project.")
        return render_template("work_form.html", projects=projects), 400

    try:
        db.create_media(
            project_id=project_id,
            file_name=file_name,
            file_type=file_type,
            file_url=file_url,
        )
    except sqlite3.IntegrityError as err:
        flash(f"Database rejected the media item: {err}")
        return render_template("work_form.html", projects=projects), 400

    return redirect(url_for("list_work"))


@app.route("/work/<int:work_id>")
def work_detail(work_id):
    work_item = db.get_media(work_id)
    if work_item is None:
        abort(404)

    return render_template("work_detail.html", work_item=work_item)


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "base.html",
            content="<h2>404 — Page Not Found</h2><p>The requested resource does not exist.</p>",
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)