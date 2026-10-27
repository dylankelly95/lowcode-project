
from flask import Flask, render_template, request, flash
import re

app = Flask(__name__)
app.secret_key = "dev-key-change-later"

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def is_valid_email(email):
    return bool(re.match(EMAIL_REGEX, email.strip()))


@app.route("/")
def home():
    return "<h1>Hello from Dylan Kelly</h1>"


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        errors = {}

        if not name:
            errors["name"] = "Full name is required."

        if not email:
            errors["email"] = "Email address is required."
        elif not is_valid_email(email):
            errors["email"] = "Please enter a valid email address."

        if not message:
            errors["message"] = "Message field cannot be empty."

        if errors:
            for error in errors.values():
                flash(error, "error")

            return render_template(
                "contact.html",
                name=name,
                email=email,
                message=message,
                errors=errors,
            ), 400

        return render_template("contact_success.html", name=name)

    return render_template("contact.html", errors={})


if __name__ == "__main__":
    app.run(debug=True)
