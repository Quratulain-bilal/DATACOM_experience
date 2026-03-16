"""Seed script to populate the database with sample data."""
from run import create_app
from app.models import db, User, Kudos, Notification

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    admin_user = User(username="admin", email="admin@datacom.com", is_admin=True, department="IT")
    admin_user.set_password("admin123")
    alice = User(username="alice", email="alice@datacom.com", department="Engineering")
    alice.set_password("password")
    bob = User(username="bob", email="bob@datacom.com", department="Marketing")
    bob.set_password("password")
    charlie = User(username="charlie", email="charlie@datacom.com", department="Engineering")
    charlie.set_password("password")
    diana = User(username="diana", email="diana@datacom.com", department="Design")
    diana.set_password("password")
    db.session.add_all([admin_user, alice, bob, charlie, diana])
    db.session.commit()

    kudos_data = [
        Kudos(sender_id=alice.id, receiver_id=bob.id, message="Great job on the client presentation! Your preparation really showed."),
        Kudos(sender_id=bob.id, receiver_id=charlie.id, message="Thanks for helping me debug that tricky issue yesterday!"),
        Kudos(sender_id=charlie.id, receiver_id=diana.id, message="Your documentation for the new API was incredibly thorough."),
        Kudos(sender_id=diana.id, receiver_id=alice.id, message="Thank you for mentoring me during my first month!"),
        Kudos(sender_id=alice.id, receiver_id=charlie.id, message="Your code review feedback always helps me grow as a developer."),
    ]
    db.session.add_all(kudos_data)
    db.session.flush()

    for k in kudos_data:
        db.session.add(Notification(user_id=k.receiver_id, kudos_id=k.id, type="kudos_received"))
    db.session.commit()

    print("Database seeded!")
    print(f"Users: {User.query.count()}, Kudos: {Kudos.query.count()}, Notifications: {Notification.query.count()}")
    print("\nCredentials: admin/admin123, alice/password, bob/password, charlie/password, diana/password")
