import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User
from keys import Password

os.environ['DATABASE_URL'] = f'postgresql://postgres:{Password}@localhost:5432/stocks-test'

from app import app

db.create_all()

#    python -m unittest test_user_model.py

class UserModelTestCase(TestCase):
    """Test the user model."""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup("firstNameTest1", "lastNameTest1", "test1", "email1@email.com", "password")
        uid1 = 111
        u1.id = uid1

        u2 = User.signup("firstNameTest2", "lastNameTest2", "test2", "email2@email.com", "password")
        uid2 = 222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):

        u = User(
            first_name="testfirst",
            last_name="testlast",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.username, "testuser")
        self.assertEqual(len(u.watchlists), 0)

# Signup Tests
    def test_valid_signup(self):
        u_test = User.signup("t1", "t1", "t1", "t1@t1.com", "password")
        uid = 444
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.first_name, "t1")
        self.assertEqual(u_test.last_name, "t1")
        self.assertEqual(u_test.username, "t1")
        self.assertEqual(u_test.email, "t1@t1.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup("t2", "t2", None, "t2@test.com", "password")
        uid = 1234
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("t2", "t2", "t2", None, "password")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("t2", "t2", "t2", "t2@test.com", "")
        
        with self.assertRaises(ValueError) as context:
            User.signup("t2", "t2", "t2", "t2@test.com", None)

# Auth test
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("wrongusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))