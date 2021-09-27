from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import String




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
    stock = db.Column(db.ARRAY(String))

    @classmethod
    def add_or_remove_stock(cls, watchlist_id, stock_ticker):
        """Add or remove a stock from the watchlist."""
        stocklist = []
        watchlist = Watchlist.query.get_or_404(watchlist_id)
        if watchlist.stock != None:
            for stock in watchlist.stock:
                stocklist.append(stock)
    
        if stock_ticker in stocklist:
            stocklist.remove(stock_ticker)
        else:
            stocklist.append(stock_ticker)
    
        watchlist.stock = stocklist
        db.session.commit()
        return watchlist

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)