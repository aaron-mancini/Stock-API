from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User table"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    watchlists = db.relationship("Watchlist")

    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up a user."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with username and password."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

class Watchlist(db.Model):
    """Watchlist will keep track of stocks based on user preferences.
        Users can have multiple watchlists.
    """

    __tablename__ = "watchlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    stocks = db.relationship("Stock", secondary="watchlists_stocks", backref="watchlists")

class Stock(db.Model):
    """Track stock info for Watchlist creation."""

    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    ticker = db.Column(db.String, nullable=False, unique=True)

class WatchlistStock(db.Model):
    """Mapping of a watchlist to stocks."""

    __tablename__ = "watchlists_stocks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlists.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)