from app import app, db, Admin

with app.app_context():
    admin = Admin(username="admin", password="admin123")
    db.session.add(admin)
    db.session.commit()
    print("ADMIN BERHASIL DIBUAT")
