from routers import Users
import os
import bcrypt
from models import salt

def create_admin(db):
    admin = Users.query.first()
    if not admin:
        admin = Users(
            username=os.environ.get('ADMIN_USERNAME'),
            email=os.environ.get('ADMIN_EMAIL'),
            password_hash=bcrypt.hashpw(os.environ.get('ADMIN_PASSWORD').encode(), salt).decode(),
            balance_RUB=1000000,
            balance_USD=10000,
            balance_EUR=9000,
            shares_HL=100,
            shares_TUBE=10
    )
    db.session.add(admin)
    db.session.commit()

