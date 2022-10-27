from app import app
from models import db, User


db.drop_all()
db.create_all()

# first_user = User.register(username= "BigChungus", password="Sam123!", email="sam@cats.com", first_name="Samantha", last_name="Huerta")


# db.session.add(first_user)
# db.session.commit()