import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Watchlist
from keys import Password

os.environ['DATABASE_URL'] = f'postgresql://postgres:{Password}@localhost:5432/stocks-test'

from app import app

db.create_all()

class WatchlistModelTestCase(TestCase):
    """Test watchlist model"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u = User.signup("test", "test", "test", "test@test.com", "password")
        self.uid = 5656
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_watchlist_model(self):
        wl = Watchlist(
            name="watchlisttest",
            description="watchlistdescription",
            user_id=self.uid
        )

        db.session.add(wl)
        db.session.commit()

        self.assertEqual(len(self.u.watchlists), 1)
        self.assertEqual(self.u.watchlists[0].name, "watchlisttest")
        self.assertEqual(self.u.watchlists[0].description, "watchlistdescription")

    def test_watchlist_stock(self):
        wl = Watchlist(
            name="watchlisttest",
            description="watchlistdescription",
            user_id=self.uid
        )
        wlid = 123
        wl.id = wlid

        db.session.add(wl)
        db.session.commit()

        Watchlist.add_or_remove_stock(wlid, "ABC")

        self.assertEqual(len(self.u.watchlists[0].stock), 1)
        self.assertEqual(self.u.watchlists[0].stock[0], "ABC")
        # should remove stock
        Watchlist.add_or_remove_stock(wlid, "ABC")

        self.assertEqual(len(self.u.watchlists[0].stock), 0)
        
