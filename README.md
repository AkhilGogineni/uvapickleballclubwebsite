[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/F1hjDb63)

Project B-08 — sportscio (Django + Channels)

Simple Django app providing a club/organization site with real-time chat and event features.

Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`

Quick setup
- Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Install dependencies:

```powershell
pip install -r requirements.txt
```

Run locally
- Apply migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

- For ASGI (Django Channels) using Daphne:

```powershell
python -m daphne -b 127.0.0.1 -p 8000 mysite.asgi:application
```

Project layout (important folders)
- `sportscio/` — main app (models, views, templates, channels consumers)
- `chat/` — chat app (real-time messaging)
- `mysite/` — Django project config (ASGI/WSGI, settings, URLs)
- `static/` and `staticfiles/` — static assets and compiled admin/static files

Notes
- Database: `db.sqlite3` (default development DB included)
- Config: update `mysite/settings.py` for production settings (SECRET_KEY, ALLOWED_HOSTS, static/media storage, database)
