"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from datetime import datetime

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


class MessageModelTestCase(TestCase):
    '''Test methods for messages'''
    
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
    def test_message_model(self):
        '''Does the message model even work?'''
        
        u = User.query.filter(User.username=='testuser').first()
        
        message = Message(
            text = 'Test text',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
        
        # u should now have 1 message
        self.assertEqual(len(u.messages), 1)
        
    def test_user_relationship(self):
        '''Test Message.user for a valid user response'''
        
        u = User.query.filter(User.username=='testuser').first()
        
        message = Message(
            text = 'Test text',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
        
        self.assertEqual(message.user, u)
        
    def test_timestamp(self):
        '''Test that valid datetime is attached to message'''
        
        u = User.query.filter(User.username=='testuser').first()
        
        message = Message(
            text = 'Test text',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
        
        #test that the time the message was created was older than the time the test is run
        self.assertLessEqual(message.timestamp, datetime.utcnow())