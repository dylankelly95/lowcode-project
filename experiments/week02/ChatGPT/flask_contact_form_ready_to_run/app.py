from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(email):
    email = email.strip()
    if not email or len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return False
    local, domain = email.rsplit("@", 1)
    if len(local) > 64:
        return False
    labels = domain.split(".")
    return all(label and len(label) <= 63 and not label.startswith("-")
               and not label.endswith("-")
               and re.fullmatch(r"[A-Za-z0-9-]+", label) for label in labels)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    values = {"name": "", "email": "", "message": ""}
    errors = {}
    if request.method == "POST":
        values = {key: request.form.get(key, "").strip()
                  for key in ("name", "email", "message")}
        if not values["name"]:
            errors["name"] = "Please enter your name."
        if not is_valid_email(values["email"]):
            errors["email"] = "Please enter a valid email address."
        if not values["message"]:
            errors["message"] = "Please enter a message."
        if not errors:
            return redirect(url_for("contact_success"))
    return render_template("contact.html", values=values, errors=errors)

@app.route("/contact/success")
def contact_success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
