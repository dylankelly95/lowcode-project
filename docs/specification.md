# Artist Portfolio Application — Specification

## Purpose

This application is for artists who want a simple way to organise and showcase their creative work in an online portfolio. It allows an artist to maintain a profile, organise work into projects, and display individual pieces of work using images, video, audio and external media links.

## Entities

### Portfolio

- `id` — integer, primary key
- `artist_name` — text, required, maximum 100 characters
- `headline` — text, optional, maximum 200 characters
- `biography` — text, optional
- `created_at` — timestamp

For this initial version, the application will manage a single sample artist portfolio. Multiple artist accounts will be introduced in a later version.

### Project

- `id` — integer, primary key
- `portfolio_id` — integer, required, foreign key referencing Portfolio
- `title` — text, required, maximum 200 characters
- `description` — text, optional
- `created_at` — timestamp

### WorkItem

- `id` — integer, primary key
- `project_id` — integer, optional, foreign key referencing Project
- `title` — text, required, maximum 200 characters
- `description` — text, optional
- `media_type` — text, one of: image, video, audio, link
- `media_url` — text, optional
- `is_featured` — integer, default 0, representing false; 1 represents true
- `created_at` — timestamp

Work items can be associated with a project or displayed individually. Media will be represented by URLs rather than uploaded files.

## Routes

| Method | Path | Does |
|---|---|---|
| GET | `/` | Display the public portfolio, artist introduction and featured work, with projects listed newest first. |
| GET | `/projects` | List all projects, newest first. |
| GET | `/projects/new` | Display a form to create a project. |
| POST | `/projects` | Validate and create a project, then redirect to `/projects`. |
| GET | `/projects/<id>` | Display a project and its associated work items. |
| GET | `/work` | List all work items, newest first. |
| GET | `/work/new` | Display a form to create a work item. |
| POST | `/work` | Validate and create a work item, then redirect to `/work`. |
| GET | `/work/<id>` | Display the details of one work item. |
| POST | `/work/<id>/feature` | Toggle whether a work item is featured, then redirect to its detail page or the work list. |

## Technical constraints

- Python 3.11 or later.
- Flask 3.x.
- SQLite using Python's standard-library `sqlite3` module; no ORM.
- Use a multi-file structure with `app.py` and HTML templates in a `templates/` directory.
- Include a shared base template, such as `templates/base.html`.
- Use Jinja2 templates for rendering pages.
- Use HTML forms and CSS for the interface. No JavaScript framework.
- No authentication in this version.
- Use parameterised SQL queries rather than building SQL statements through string concatenation.
- Validate form inputs on the server, including required titles, maximum title lengths and supported media types.
- Handle missing project and work-item IDs with an appropriate 404 response.
- Use external media URLs rather than file uploads.
- Keep the application straightforward to install and run locally.

## Out of scope

- User registration, login and authentication.
- Multiple artist accounts and role-based access.
- Direct image, audio or video uploads.
- Customisable colour themes and fonts.
- Likes, comments, follows and visitor accounts.
- Artist discovery, search and recommendations.
- Contact forms and messaging.
- Scheduled, event-triggered and approval automations.
- External APIs and payment processing.
- Custom domains and subdomains.

These features may be introduced in later versions, subject to the requirements of the overall CCT College project.

## Initial acceptance criteria

- The application starts successfully using the documented setup instructions.
- The homepage displays the sample artist profile and featured work.
- Projects can be created and listed.
- Work items can be created, listed and viewed individually.
- Work items can be associated with projects or left ungrouped.
- A work item can be marked as featured or unfeatured.
- Data persists in SQLite when the application restarts.
- Invalid form input is handled with a visible error message.
- The application uses multiple files and a shared base template.
- The application runs without requiring authentication or a JavaScript framework.

