from app import db
from models import User, Stock, Watchlist, WatchlistStock

db.drop_all()
db.create_all()

db.session.commit()