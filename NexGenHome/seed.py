# seed.py
from app import app, db, User  # import your app, db, User from app.py

# Make sure to run inside app context
with app.app_context():
    # Drop existing tables and create fresh ones
    db.drop_all()
    db.create_all()

    # Create admin user
    admin = User(username="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Admin created -> username: admin | password: admin123")