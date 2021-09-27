import os
from unittest import TestCase

from models import db, connect_db, User, Watchlist
from keys import Password

os.environ['DATABASE_URL'] = f'postgresql://postgres:{Password}@localhost:5432/stocks-test'

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UsesViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(first_name="test",
                                    last_name="test",
                                    username="test",
                                    email="test@test.com",
                                    password="password")
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_homepage(self):
        with self.client as c:
            resp = c.get("/")

            self.assertIn("Log in", str(resp.data))
            self.assertNotIn("Watchlists", str(resp.data))

    def test_user_homepage(self):
        wl = Watchlist(name="Wltest", description="this is a test.", user_id=self.testuser_id)
        db.session.add(wl)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("/")

            self.assertIn("watchlists", str(resp.data))
            self.assertIn("Wltest", str(resp.data))

    def test_stock(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("/stocks/AAPL") 

            self.assertIn("AAPL", str(resp.data))   
            self.assertIn("Apple", str(resp.data))
            self.assertIn("Add to watchlist", str(resp.data))

    

