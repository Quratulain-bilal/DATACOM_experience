# 🏆 Kudos System — Datacom Internal Employee Portal

A web application that allows employees to give public kudos (appreciation messages) to their colleagues, with admin content moderation.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data
python seed.py

# Run the application
python run.py
```

Then visit: **http://localhost:5000**

## Login Credentials (after seeding)

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| alice | password | User |
| bob | password | User |
| charlie | password | User |
| diana | password | User |

## Features

- ✅ User registration and authentication
- ✅ Give kudos to colleagues with appreciation messages
- ✅ Public feed of recent kudos on dashboard
- ✅ Character counter (max 500 chars)
- ✅ Duplicate submission prevention (5-min window)
- ✅ Admin moderation panel (hide/restore/delete kudos)
- ✅ Responsive Bootstrap 5 UI
- ✅ Pagination on feed and admin panel

## Project Structure

```
Task Two/
├── SPECIFICATION.md      # Full specification document
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── run.py                # Application entry point
├── seed.py               # Database seeder
└── app/
    ├── __init__.py
    ├── models.py         # SQLAlchemy models (User, Kudos)
    ├── forms.py          # WTForms definitions
    ├── routes.py         # Flask routes and blueprints
    └── templates/
        ├── base.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── give_kudos.html
        └── admin/
            └── moderation.html
```
