from app import db
from models import User, Watchlist

db.drop_all()
db.create_all()

db.session.commit()

