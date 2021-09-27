import os
import requests
from unittest import TestCase

from flask import Flask, request
from models import db, connect_db, User, Watchlist
from keys import Password

os.environ['DATABASE_URL'] = f'postgresql://postgres:{Password}@localhost:5432/stocks-test'

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class WatchlistViewTestCase(TestCase):
    """Test watchlist views."""

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

        wl = Watchlist(id=555, name="Wltest", description="this is a test.", user_id=self.testuser_id)
        db.session.add(wl)

        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_watchlist_route(self):
        with self.client as c:
            resp = c.get("watchlists/555", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized.", str(resp.data))

    def test_user_watchlist_route(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("watchlists/555")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("this is a test.", str(resp.data))

    def test_create_watchlist(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/create/watchlist", data={"name": "Test", "description": "test description"})

            self.assertEqual(resp.status_code, 302)

            wl = Watchlist.query.filter_by(name="Test").first()
            self.assertEqual(wl.name, "Test")

    def test_delete_watchlist(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/delete/watchlist/555", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            wl = Watchlist.query.get(555)
            self.assertIsNone(wl)

    def test_unauthorized_delete_watchlist(self):

        u = User.signup(first_name="testuser",
                        last_name="testuser",
                        username="testuser",
                        email="testuser@test.com",
                        password="password")
        u.id = 111

        wl = Watchlist(id=777,
                        name="testwl",
                        description="testdescript",
                        user_id=self.testuser_id)
        db.session.add_all([u,wl])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 111

            resp = c.post("/delete/watchlist/777", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Watchlist.query.get(777)
            self.assertIsNotNone(m)

    def test_watchlist_delete_no_auth(self):

        wl = Watchlist(
            id=9876,
            name="test wl",
            description="test description",
            user_id=self.testuser_id
        )
        db.session.add(wl)
        db.session.commit()

        with self.client as c:
            resp = c.post("/delete/watchlist/9876", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            wl = Watchlist.query.get(9876)
            self.assertIsNotNone(wl)

    # def test_update_watchlist(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         resp = requests.request("POST", "http://127.0.0.1:5000/update-watchlist", params={"watchlist": 555, "ticker":"AAPL"})

    #         wl = Watchlist.query.get(555)
    #         self.assertEqual(wl.stock, 1)