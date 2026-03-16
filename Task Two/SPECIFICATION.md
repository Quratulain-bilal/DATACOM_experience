# Kudos System Specification

## 1. Overview
An internal web application feature that allows employees at Datacom to give public "kudos" (messages of appreciation) to their colleagues. The system includes a public feed, user authentication, and admin content moderation.

---

## 2. Functional Requirements

### 2.1 User Stories

| ID | Role | Story | Priority |
|----|------|-------|----------|
| US-1 | User | As a user, I can log in with my employee credentials | High |
| US-2 | User | As a user, I can select another user from a dropdown list of colleagues | High |
| US-3 | User | As a user, I can write a short message of appreciation (max 500 characters) | High |
| US-4 | User | As a user, I can submit the kudos which gets stored in the database | High |
| US-5 | User | As a user, I can view a public feed of recent kudos on the main dashboard | High |
| US-6 | User | As a user, I cannot send kudos to myself | Medium |
| US-7 | User | As a user, I can see who gave kudos and who received them, with timestamps | Medium |
| US-8 | Admin | As an administrator, I can hide inappropriate kudos messages from the public feed | High |
| US-9 | Admin | As an administrator, I can permanently delete inappropriate kudos messages | High |
| US-10 | Admin | As an administrator, I can view all kudos including hidden ones in a moderation panel | High |
| US-11 | Admin | As an administrator, I can restore previously hidden kudos | Medium |

### 2.2 Acceptance Criteria

**US-1: Authentication**
- Users can register with username, email, and password
- Users can log in and log out
- Passwords are hashed and stored securely
- Sessions persist until logout

**US-2: User Selection**
- Dropdown displays all registered users except the logged-in user
- Users are listed alphabetically by name

**US-3: Kudos Message**
- Text area with 500-character limit
- Character counter displayed to user
- Message cannot be empty or whitespace-only

**US-4: Submit Kudos**
- Kudos is saved with sender_id, receiver_id, message, and timestamp
- Success confirmation displayed after submission
- Duplicate submissions (same sender, receiver, message) within 5 minutes are blocked

**US-5: Public Feed**
- Shows most recent kudos first (newest on top)
- Paginated: 20 kudos per page
- Only shows kudos where `is_visible = true`
- Displays sender name, receiver name, message, and relative timestamp

**US-8/9/10: Content Moderation**
- Admin panel accessible only to users with `is_admin = true`
- Admin can toggle visibility (hide/show) of any kudos
- Admin can permanently delete kudos
- Moderation actions are logged with `moderated_by`, `moderated_at`, and `moderation_reason`

---

## 3. Technical Design

### 3.1 Technology Stack
- **Backend**: Python (Flask)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Frontend**: HTML, CSS (Bootstrap 5), Jinja2 templates
- **Authentication**: Flask-Login with Werkzeug password hashing

### 3.2 Database Schema

#### Table: `users`
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| username | VARCHAR(80) | UNIQUE, NOT NULL |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(256) | NOT NULL |
| is_admin | BOOLEAN | DEFAULT false |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### Table: `kudos`
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| sender_id | INTEGER | FOREIGN KEY → users.id, NOT NULL |
| receiver_id | INTEGER | FOREIGN KEY → users.id, NOT NULL |
| message | TEXT | NOT NULL, max 500 chars |
| is_visible | BOOLEAN | DEFAULT true |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| moderated_by | INTEGER | FOREIGN KEY → users.id, NULLABLE |
| moderated_at | DATETIME | NULLABLE |
| moderation_reason | VARCHAR(255) | NULLABLE |

### 3.3 API Endpoints / Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Redirect to login or dashboard |
| GET | `/register` | No | Registration page |
| POST | `/register` | No | Create new user |
| GET | `/login` | No | Login page |
| POST | `/login` | No | Authenticate user |
| GET | `/logout` | Yes | Log out user |
| GET | `/dashboard` | Yes | Main dashboard with kudos feed |
| GET | `/give-kudos` | Yes | Kudos creation form |
| POST | `/give-kudos` | Yes | Submit new kudos |
| GET | `/admin/moderation` | Admin | Moderation panel (all kudos) |
| POST | `/admin/hide/<id>` | Admin | Toggle kudos visibility |
| POST | `/admin/delete/<id>` | Admin | Permanently delete kudos |

### 3.4 Frontend Components
1. **Login/Register Pages** — Simple forms with validation
2. **Dashboard** — Navigation bar + paginated kudos feed
3. **Give Kudos Form** — User dropdown + message textarea + character counter
4. **Admin Moderation Panel** — Table of all kudos with hide/delete actions

### 3.5 Security Considerations
- Passwords hashed with Werkzeug `generate_password_hash`
- Flask-Login for session management
- CSRF protection via Flask-WTF
- Input sanitization (HTML escape all user content)
- Admin routes protected by `@admin_required` decorator
- SQL injection prevented by SQLAlchemy ORM

### 3.6 Performance Considerations
- Pagination on feed (20 per page)
- Database indexes on `kudos.created_at` and `kudos.is_visible`
- Lazy loading of user relationships

---

## 4. Implementation Plan

| Step | Task | Dependencies |
|------|------|-------------|
| 1 | Project setup (Flask, SQLAlchemy, Flask-Login) | None |
| 2 | Database models (User, Kudos) | Step 1 |
| 3 | User registration and login | Step 2 |
| 4 | Dashboard with kudos feed | Step 3 |
| 5 | Give kudos form and submission | Step 3 |
| 6 | Admin moderation panel | Step 4 |
| 7 | Input validation and error handling | Steps 3-6 |
| 8 | UI styling with Bootstrap | Steps 3-6 |
| 9 | Testing | All steps |

---

## 5. Specification Approval

✅ **APPROVED** — This specification has been reviewed, refined with content moderation requirements, and approved for implementation.
