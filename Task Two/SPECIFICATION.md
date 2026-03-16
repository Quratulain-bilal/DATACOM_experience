# Kudos System Specification

## Functional Requirements

### User Stories

#### Core Kudos Functionality

1. **As a user**, I can select another user from a dropdown list of colleagues
2. **As a user**, I can write a message of appreciation (max 500 characters)
3. **As a user**, I can submit the kudos which gets stored in the database
4. **As a user**, I can view a feed of recent kudos on the dashboard
5. **As a user**, I can see my own kudos history and statistics

#### User Authentication and Management

6. **As a user**, I can log in with my company credentials
7. **As a user**, I can view my profile and kudos statistics
8. **As a user**, I can see who has given me kudos and when

#### Content Moderation

9. **As an administrator**, I can hide or delete inappropriate kudos messages
10. **As an administrator**, I can view all kudos for moderation purposes
11. **As an administrator**, I can restore hidden kudos if needed
12. **As a user**, I can report inappropriate kudos for review

#### Additional Features

13. **As a user**, I can search for kudos by recipient or sender
14. **As a user**, I can filter kudos by date range
15. **As a user**, I can receive notifications when someone gives me kudos

### Acceptance Criteria

#### User Story 1: User Selection

- Dropdown shows all active employees (excluding self)
- Users are sorted alphabetically by name
- Shows user's name and department
- Handles cases where no users are available

#### User Story 2: Message Creation

- Text area accepts up to 500 characters
- Real-time character count display
- Prevents submission of empty messages
- Supports basic formatting (line breaks)

#### User Story 3: Kudos Submission

- Stores kudos with timestamp, sender, recipient, and message
- Validates all required fields before submission
- Shows success confirmation message
- Handles submission errors gracefully
- Prevents duplicate submissions within 5-minute window

#### User Story 4: Kudos Feed

- Displays most recent kudos first (paginated, 20 per page)
- Shows sender, recipient, message, and timestamp
- Hides moderated kudos from regular users
- Responsive design for mobile and desktop

#### User Story 5: Personal History

- Shows kudos received and given separately
- Displays kudos statistics (total received, total given)
- Allows filtering by date range
- Shows kudos details on click

#### User Story 6: Authentication

- Secure login with username and password
- Maintains user session securely
- Handles login/logout gracefully
- Redirects unauthenticated users to login

#### User Story 7: User Profile

- Shows user's kudos statistics
- Displays recent kudos activity
- Shows department and join date
- Allows basic profile editing

#### User Story 8: Kudos Received

- Lists all kudos received by the user
- Shows sender information and timestamp
- Allows sorting by date
- Includes message content

#### User Story 9: Content Moderation

- Admin can hide kudos (sets is_visible = false)
- Admin can permanently delete kudos
- Moderation actions are logged with admin ID and timestamp
- Hidden kudos are not visible to regular users

#### User Story 10: Admin Dashboard

- Shows all kudos with moderation controls
- Displays moderation status for each kudos
- Allows bulk moderation actions
- Shows moderation statistics

#### User Story 11: Restore Functionality

- Admin can restore hidden kudos
- Restored kudos become visible to all users
- Restoration is logged with admin ID and timestamp
- Shows restoration history

#### User Story 12: Report System

- Users can report inappropriate kudos
- Reports are queued for admin review
- Report includes reporter ID and reason
- Admins are notified of new reports

#### User Story 13: Search Functionality

- Search by recipient name or sender name
- Real-time search results
- Highlights matching text
- Handles partial matches

#### User Story 14: Date Filtering

- Filter by date range (last week, month, year)
- Custom date range selection
- Maintains filter state across page navigation
- Shows filtered results count

#### User Story 15: Notifications

- In-app notification when receiving kudos
- Notification badge on navigation bar
- Notification preferences settings
- Mark notifications as read

## Technical Design

### Database Schema

#### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    department VARCHAR(100),
    join_date DATE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Kudos Table

```sql
CREATE TABLE kudos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_visible BOOLEAN DEFAULT TRUE,
    moderated_by INTEGER,
    moderated_at TIMESTAMP,
    moderation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id),
    FOREIGN KEY (moderated_by) REFERENCES users(id)
);
```

#### Reports Table

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kudos_id INTEGER NOT NULL,
    reporter_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kudos_id) REFERENCES kudos(id),
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);
```

#### Notifications Table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kudos_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (kudos_id) REFERENCES kudos(id)
);
```

### API Endpoints

#### Authentication

- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /register` - Registration page
- `POST /register` - Create new user
- `GET /logout` - Log out user

#### Kudos Management

- `GET /dashboard` - Main dashboard with kudos feed (paginated)
- `GET /give-kudos` - Kudos creation form
- `POST /give-kudos` - Submit new kudos
- `GET /my-kudos` - Personal kudos history
- `GET /profile/<id>` - User profile with kudos stats

#### Search and Filter

- `GET /search?q=<term>` - Search kudos by sender/receiver name
- `GET /dashboard?filter=week|month|year` - Filter kudos by date range

#### Moderation (Admin Only)

- `GET /admin/moderation` - Moderation panel with all kudos
- `POST /admin/hide/<id>` - Toggle kudos visibility (hide/restore)
- `POST /admin/delete/<id>` - Permanently delete kudos
- `GET /admin/reports` - View reported kudos queue

#### Reports

- `POST /report/<kudos_id>` - Report inappropriate kudos
- `POST /admin/reports/<id>/resolve` - Resolve a report

#### Notifications

- `GET /notifications` - View user notifications
- `POST /notifications/<id>/read` - Mark notification as read
- `POST /notifications/read-all` - Mark all notifications as read

### Frontend Components

#### Core Components

- `KudosForm` - Form for creating new kudos with user dropdown and character counter
- `KudosFeed` - Paginated display feed of recent kudos
- `KudosCard` - Individual kudos display card with sender, receiver, message, timestamp
- `UserDropdown` - Alphabetically sorted user selection (excludes self)
- `CharacterCounter` - Real-time character count (turns red at 450+)

#### User Components

- `UserProfile` - User profile page with kudos statistics
- `KudosHistory` - Personal kudos history (sent and received tabs)
- `UserSearch` - Search bar for finding kudos by name
- `NotificationBadge` - Notification count badge in navbar

#### Admin Components

- `ModerationPanel` - Admin moderation interface with hide/delete/restore controls
- `ReportsQueue` - Reports management table with resolve actions
- `AdminDashboard` - Admin overview with moderation statistics

#### Navigation Components

- `Navbar` - Main navigation header with links and notification badge
- `Pagination` - Page navigation for kudos feed and admin panel
- `FlashMessages` - Alert system for success/error/warning messages

### Security Considerations

#### Authentication & Authorization

- Password hashing with Werkzeug `generate_password_hash` (pbkdf2:sha256)
- Flask-Login for session management
- Role-based access control (user/admin) via `is_admin` field
- `@login_required` decorator for protected routes
- `@admin_required` custom decorator for admin-only routes
- CSRF protection via Flask-WTF on all forms

#### Input Validation

- Server-side validation for all form inputs (WTForms validators)
- Maximum message length enforced (500 characters)
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)
- XSS protection via Jinja2 auto-escaping and `markupsafe.escape()`
- Duplicate submission prevention (5-minute cooldown)
- Self-kudos prevention (cannot select yourself)

#### Data Protection

- Audit logging for all moderation actions (who, when, reason)
- Passwords never stored in plaintext
- Session cookies with secure flags

### Performance Considerations

#### Database Optimization

- Indexed foreign keys on `kudos.sender_id`, `kudos.receiver_id`
- Index on `kudos.created_at` for efficient feed sorting
- Index on `kudos.is_visible` for fast feed filtering
- Pagination for all list views (20 items for feed, 50 for admin)
- Efficient queries with SQLAlchemy lazy loading

#### Frontend Optimization

- Bootstrap 5 via CDN (cached by browser)
- Minimal JavaScript (character counter only)
- Responsive design for mobile and desktop
- Server-side rendering with Jinja2 (no SPA overhead)

## Implementation Plan

### Phase 1: Core Functionality (Foundation)

1. Set up Flask project structure with blueprints
2. Configure SQLAlchemy with SQLite database
3. Create database models (User, Kudos, Report, Notification)
4. Implement user registration and login with Flask-Login
5. Build base HTML template with Bootstrap 5 navbar

### Phase 2: User Interface (Kudos Features)

1. Implement Give Kudos form with user dropdown and character counter
2. Build Dashboard with paginated kudos feed
3. Create user profile page with kudos statistics
4. Add personal kudos history (sent and received)
5. Implement search and date filtering on feed

### Phase 3: Moderation System (Admin Features)

1. Build admin moderation panel with all kudos listed
2. Implement hide/restore toggle with moderation logging
3. Implement permanent delete with confirmation
4. Create reporting system (user reports + admin review queue)
5. Add notification system (in-app badges)

### Phase 4: Testing and Polish

1. Unit tests for all models and business logic
2. Integration tests for all routes and forms
3. Edge case testing (empty data, invalid input, unauthorized access)
4. UI polish and responsive design verification
5. Documentation and README

### Testing Strategy

- **Unit tests**: Model methods (password hashing, relationships)
- **Integration tests**: All route responses (status codes, redirects)
- **Form tests**: Validation rules (required fields, max length, self-kudos)
- **Auth tests**: Login, logout, protected routes, admin access
- **Moderation tests**: Hide, restore, delete, report workflows

### Deployment Considerations

- SQLite for development (easy setup, no external dependencies)
- Environment variables for secret key in production
- Debug mode disabled in production
- Git repository with `.gitignore` for `__pycache__`, `*.db`, `.env`

## Success Metrics

### User Engagement

- Daily active users giving/receiving kudos
- Kudos submission rate (target: 5+ per day per 100 users)
- User retention rate
- Feature adoption rate across departments

### System Performance

- Page load times (< 2 seconds)
- Form submission response (< 500ms)
- System uptime (> 99.9%)
- Error rate (< 0.1%)

### Content Quality

- Report rate (< 1% of kudos)
- Moderation queue size (< 10 pending at any time)
- User satisfaction scores
- Content appropriateness metrics

---

This specification provides a comprehensive blueprint for building a robust, scalable, and user-friendly Kudos system that meets all business requirements while maintaining high standards for security, performance, and user experience.
