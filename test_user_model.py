"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    def test_is_following(self):
        """Detection of when one user is following another user"""
        
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        db.session.add(user2)
        db.session.commit()
        
        # Test no following relationship between user1 and user2
        self.assertEqual(user1.is_following(user2), False)
        
        # user1 starts following user2
        test_follow = Follows(user_being_followed_id=user2.id, user_following_id=user1.id)
        db.session.add(test_follow)
        db.session.commit()
        
        self.assertEqual(user1.is_following(user2), True)
        
        
    def test_is_followed_by(self):
        """Detection of users followers"""
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        db.session.add(user2)
        db.session.commit()
        
        # test that user2 is not following user1
        self.assertEqual(user1.is_followed_by(user2), False)
        
        # user2 followed user1 back, test that user
        follow_back = Follows(user_being_followed_id=user1.id, user_following_id=user2.id)
        db.session.add(follow_back)
        db.session.commit()
        self.assertEqual(user1.is_followed_by(user2), True)
        
    def test_signup(self):
        '''Test signup classmethod'''
        
        user = User.signup(username='test', password='testpassword', email="test@email.com", image_url='test.url.png')
        db.session.commit()
        #Test that user was created
        self.assertEqual(user.username, 'test')
        self.assertEqual(f'{User.query.get(user.id)}', f'<User #{user.id}: test, test@email.com>')
        
        #Test that user isn't created if .signup is missing positional arguments
        self.assertRaises(TypeError, User.signup, username='test1')
        
    def test_authenticate(self):
        '''Test user authentication'''
        
        user1 = User.signup(username='testuser1', password="HASHED_PASSWORD1", email='test@test.gmail.com', image_url='test_img.png')
        db.session.commit()
        
        # Returns correct user, if found
        self.assertEqual(User.authenticate(username='testuser1', password="HASHED_PASSWORD1"), User.query.get(user1.id))
        
        # Does not return user when not found
        self.assertNotEqual(User.authenticate(username='WRONG_USERNAME', password="HASHED_PASSWORD1"), User.query.get(user1.id))
        self.assertNotEqual(User.authenticate(username='testuser1', password="WRONG_PASSWORD"), User.query.get(user1.id))