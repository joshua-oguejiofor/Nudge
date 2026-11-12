# Nudge

> A personal to-do app that doesn't just store your tasks, it **nudges you** to finish them.

Nudge is a Flask to-do list with email-verified accounts and a background worker that emails you a reminder every few hours. I built it for my own use and as a way to add to my Flask experince (auth, migrations, background jobs).

## Features

- **Accounts** with email verification (one-time code) and Argon2 password hashing
- **Password reset** via emailed code
- **Tasks**: create, view, update, delete, search, and tick off as done
- **Priorities**: low, medium, high, urgent
- **Email reminders** every 6 hours for medium and urgent tasks (Celery Beat)
- Responsive UI with a mobile menu and auto-fading flash messages

## Tech stack

| Area | Tools |
| --- | --- |
| Web | Flask, Jinja2, Flask-Login |
| Database | SQLAlchemy 2, Flask-SQLAlchemy, Flask-Migrate (Alembic), SQLite or MySQL (PyMySQL) |
| Security | Argon2 (`argon2-cffi`) |
| Background jobs | Celery |
| Email | `smtplib` (SMTP with STARTTLS) |

## Project structure

```
.
├── app/
│   ├── main.py            # Flask app setup, login manager, global error handler
│   ├── auth.py            # register, verify code, login, reset/change password, logout
│   ├── route.py           # todo routes (home, view, update, delete, search, toggle)
│   ├── model.py           # User and Todo models
│   ├── utility.py         # TaskPriority enum
│   ├── config.py          # settings read from .env
│   ├── extensions.py      # db, migrate, login_manager
│   ├── email_server.py    # SMTP helpers + HTML email templates
│   ├── workers/
│   │   ├── celery_config.py   # Celery app + beat schedule
│   │   └── tasks.py           # send_otp, send_todo_reminders_task
│   ├── templates/         # base.html + auth/ and todo/ pages
│   └── static/            # css/ and js/
├── migrations/            # Alembic migrations
├── .env.example
└── requirements.txt
```

## Getting started

**Requirements:** Python 3.11+ (uses `StrEnum`), and an SMTP account (e.g. a Gmail app password).

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your environment
cp .env.example .env             # then fill in the values (see below)

# 4. Create the database tables
flask --app app.main db upgrade

# 5. Run the app
flask --app app.main run --debug
```

Open <http://127.0.0.1:5000/login>.

### Environment variables

| Variable | Description | Example |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///todo.db` or `mysql+pymysql://user:pass@localhost/nudge` |
| `SECRET_KEY` | Signs session cookies. Use a long random string | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SMTP_HOST` | SMTP server (port 587 + STARTTLS is used) | `smtp.gmail.com` |
| `SMTP_USER` | SMTP login, also the "From" address | `you@gmail.com` |
| `SMTP_PASSWORD` | SMTP password / app password | |
| `TO_USER` | Address that **all** emails are sent to (codes and reminders) | `you@gmail.com` |
| `CELERY_BROKER` | Celery broker URL | `redis://localhost:6379/0` or `sqlite`|
| `CELERY_BACKEND` | Celery result backend URL | `redis://localhost:6379/1` or `sqlite`|


### Background worker (codes and reminders)

Verification codes are sent by Celery, so the worker must be running for sign-up and password reset to work.

```bash
# worker: sends verification codes and reminder emails
celery -A app.workers.celery_config.celery_app worker --loglevel=info

# beat: schedules the reminder email every 6 hours
celery -A app.workers.celery_config.celery_app beat --loglevel=info
```

## How it works

1. **Sign up:** the form data is held in the session and a code is emailed. The account is only created once the correct code is entered.
2. **Log in:** passwords are checked against the Argon2 hash. A single generic error is shown for a wrong email or a wrong password.
3. **Reset password:** enter your email, enter the emailed code, then choose a new password.
4. **Sessions** for the verification steps expire after 10 minutes.

### Routes

| Route | Methods | Login needed | Purpose |
| --- | --- | --- | --- |
| `/login` | GET, POST | no | Log in (first page) |
| `/Register` | GET, POST | no | Sign up |
| `/verify_code` | GET, POST | no | Enter emailed code |
| `/reset_password` | GET, POST | no | Request a reset code |
| `/change-password` | GET, POST | no | Set a new password |
| `/logout` | GET | yes | Log out |
| `/home` | GET, POST | yes | List and add tasks |
| `/view/<id>` | GET | yes | View one task |
| `/update/<id>` | GET, POST | yes | Edit a task |
| `/delete/<id>` | GET | yes | Delete a task |
| `/toggle/<id>` | POST | yes | Mark done / not done |
| `/search` | POST | yes | Search by title |


