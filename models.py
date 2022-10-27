from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User class"""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    feedback = db.relationship('Feedback', backref="user", cascade="all, delete-orphan")


    def __repr__(self):
        """Show info about user."""
        u = self
        return f"<User {u.username} {u.email} {u.first_name} {u.last_name}>"

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False."""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False


class Feedback(db.Model):
    """Feedback class"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)

    def __repr__(self):
        """Show info about user feedback."""
        f = self
        return f"<User {f.id} {f.title} {f.content} {f.username}>"
