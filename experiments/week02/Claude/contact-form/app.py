"""Contact form for Flask 3.x. Uses only Flask and the standard library."""

import os
import re
import secrets

from flask import Flask, abort, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
# Set SECRET_KEY in the environment for production. The fallback key changes
# on every restart, which is fine for development but invalidates sessions.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

NAME_MAX = 100
EMAIL_MAX = 254  # practical maximum length of an email address
MESSAGE_MAX = 5000

# Pragmatic server-side check: one "@", a non-empty local part, and a domain
# of dot-separated labels ending in an alphabetic TLD of at least 2 characters.
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}$"
)

BASE_STYLE = """
  body { font-family: system-ui, sans-serif; max-width: 36rem; margin: 3rem auto; padding: 0 1rem; color: #222; }
  label { display: block; margin-top: 1rem; font-weight: 600; }
  input, textarea { width: 100%; padding: .5rem; margin-top: .25rem; font: inherit; box-sizing: border-box; }
  textarea { min-height: 9rem; }
  button { margin-top: 1.25rem; padding: .6rem 1.2rem; font: inherit; cursor: pointer; }
  .error { color: #b00020; margin: .25rem 0 0; font-size: .9rem; }
  .invalid { border: 1px solid #b00020; }
  .summary { background: #fdecea; border: 1px solid #b00020; padding: .75rem 1rem; border-radius: 4px; }
"""

CONTACT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contact us</title>
  <style>{{ style }}</style>
</head>
<body>
  <h1>Contact us</h1>

  {% if errors %}
    <div class="summary" role="alert">Please fix the errors below and try again.</div>
  {% endif %}

  <form method="post" action="{{ url_for('contact') }}" novalidate>
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">

    <label for="name">Name</label>
    <input type="text" id="name" name="name" value="{{ values.name }}"
           maxlength="{{ name_max }}" class="{{ 'invalid' if errors.name }}"
           {% if errors.name %}aria-invalid="true" aria-describedby="name-error"{% endif %}>
    {% if errors.name %}<p class="error" id="name-error">{{ errors.name }}</p>{% endif %}

    <label for="email">Email</label>
    <input type="email" id="email" name="email" value="{{ values.email }}"
           maxlength="{{ email_max }}" class="{{ 'invalid' if errors.email }}"
           {% if errors.email %}aria-invalid="true" aria-describedby="email-error"{% endif %}>
    {% if errors.email %}<p class="error" id="email-error">{{ errors.email }}</p>{% endif %}

    <label for="message">Message</label>
    <textarea id="message" name="message" maxlength="{{ message_max }}"
              class="{{ 'invalid' if errors.message }}"
              {% if errors.message %}aria-invalid="true" aria-describedby="message-error"{% endif %}>{{ values.message }}</textarea>
    {% if errors.message %}<p class="error" id="message-error">{{ errors.message }}</p>{% endif %}

    <button type="submit">Send message</button>
  </form>
</body>
</html>
"""

THANKS_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Message sent</title>
  <style>{{ style }}</style>
</head>
<body>
  <h1>Thank you{% if name %}, {{ name }}{% endif %}!</h1>
  <p>Your message has been received.</p>
  <p><a href="{{ url_for('contact') }}">Send another message</a></p>
</body>
</html>
"""


def get_csrf_token() -> str:
    """Return the session's CSRF token, creating one if needed."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate(name: str, email: str, message: str) -> dict:
    """Return a dict of field -> error message (empty if everything is valid)."""
    errors = {}

    if not name:
        errors["name"] = "Please enter your name."
    elif len(name) > NAME_MAX:
        errors["name"] = f"Name must be {NAME_MAX} characters or fewer."

    if not email:
        errors["email"] = "Please enter your email address."
    elif len(email) > EMAIL_MAX or not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."

    if not message:
        errors["message"] = "Please enter a message."
    elif len(message) > MESSAGE_MAX:
        errors["message"] = f"Message must be {MESSAGE_MAX} characters or fewer."

    return errors


@app.route("/contact", methods=["GET", "POST"])
def contact():
    values = {"name": "", "email": "", "message": ""}
    errors = {}

    if request.method == "POST":
        expected = session.get("csrf_token")
        submitted = request.form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected, submitted):
            abort(400, description="Invalid or missing CSRF token. Reload the page and try again.")

        values = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "message": request.form.get("message", "").strip(),
        }
        errors = validate(**values)

        if not errors:
            # Nothing is stored for now. Hook in email sending or storage here later.
            session["thanks_name"] = values["name"]
            # Post/Redirect/Get so a refresh doesn't resubmit the form.
            return redirect(url_for("contact_thanks"))

    status = 422 if errors else 200
    return (
        render_template_string(
            CONTACT_TEMPLATE,
            style=BASE_STYLE,
            values=values,
            errors=errors,
            csrf_token=get_csrf_token(),
            name_max=NAME_MAX,
            email_max=EMAIL_MAX,
            message_max=MESSAGE_MAX,
        ),
        status,
    )


@app.route("/contact/thanks")
def contact_thanks():
    name = session.pop("thanks_name", "")
    return render_template_string(THANKS_TEMPLATE, style=BASE_STYLE, name=name)


if __name__ == "__main__":
    app.run(debug=True)
