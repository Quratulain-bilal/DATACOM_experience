"""Seed script to populate the database with sample data."""

from run import create_app
from app.models import db, User, Kudos

app = create_app()

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create users
    admin_user = User(username="admin", email="admin@datacom.com", is_admin=True)
    admin_user.set_password("admin123")

    alice = User(username="alice", email="alice@datacom.com")
    alice.set_password("password")

    bob = User(username="bob", email="bob@datacom.com")
    bob.set_password("password")

    charlie = User(username="charlie", email="charlie@datacom.com")
    charlie.set_password("password")

    diana = User(username="diana", email="diana@datacom.com")
    diana.set_password("password")

    db.session.add_all([admin_user, alice, bob, charlie, diana])
    db.session.commit()

    # Create sample kudos
    kudos_data = [
        Kudos(sender_id=alice.id, receiver_id=bob.id, message="Great job on the client presentation! Your preparation really showed."),
        Kudos(sender_id=bob.id, receiver_id=charlie.id, message="Thanks for helping me debug that tricky issue yesterday. Couldn't have done it without you!"),
        Kudos(sender_id=charlie.id, receiver_id=diana.id, message="Your documentation for the new API was incredibly thorough and helpful."),
        Kudos(sender_id=diana.id, receiver_id=alice.id, message="Thank you for mentoring me during my first month. You made the transition so smooth!"),
        Kudos(sender_id=alice.id, receiver_id=charlie.id, message="Your code review feedback is always constructive and helps me grow as a developer."),
    ]
    db.session.add_all(kudos_data)
    db.session.commit()

    print("Database seeded successfully!")
    print(f"Users: {User.query.count()}")
    print(f"Kudos: {Kudos.query.count()}")
    print("\nLogin credentials:")
    print("  Admin: admin / admin123")
    print("  Users: alice, bob, charlie, diana / password")
