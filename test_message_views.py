"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from cgi import test
import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
# app.config['TESTING'] = True


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.commit()
        
    def tearDown(self):
        '''Clean up potential bad transactions'''
        db.session.rollback()

    def test_add_message_logged_out(self):
        # First try without logging in
        with self.client as c:
            resp = c.post('/messages/new', data={'text': 'Should not work'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>What\'s Happening?</h1>', html)
    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_message_destroy_logged_out(self):
        u = User.query.filter(User.username=='testuser').first()
        
        message = Message(
            text = 'Test text',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
        
        with self.client as c:
            resp = c.post(f'/messages/{message.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
    def test_message_destroy(self):
        '''Can a user delete a message?'''
        
        u = User.query.filter(User.username=='testuser').first()
        
        message = Message(
            text = 'Test text',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
       
        with self.client as client:
            with client.session_transaction() as sess:
                u = User.query.filter(User.username=='testuser').first()
                message = Message.query.filter_by(user_id=u.id).first()
                sess[CURR_USER_KEY] = self.testuser.id
            resp = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Test text', html)
            
    def test_message_destroy_for_other_user(self):
        '''Can a user delete another user's messages?'''
        # create message for test user
        u = User.query.filter(User.username=='testuser').first()
        message = Message(
            text = 'This message should still exist.',
            user_id = u.id
        )
        db.session.add(message)
        db.session.commit()
        # add second user
        investigator = User.signup(username="investigator",
                                email="test2@test2.com",
                                password="detective",
                                image_url=None)
        db.session.add(investigator)
        db.session.commit()
        
        # login second user 
        with self.client as client:
            with client.session_transaction() as sess:
                investigator = User.query.filter(User.username=='investigator').first()
                testuser = User.query.filter(User.username=='testuser').first()
                sess[CURR_USER_KEY] = investigator.id
            msg = Message.query.one()
            resp = client.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            # check that message wasn't deleted
            self.assertIn('This message should still exist.', html)
        
    def test_add_message_for_other_user(self):
        '''Can a logged in user add a message for another user?'''
        
        investigator = User.signup(username="investigator",
                                email="test2@test2.com",
                                password="detective",
                                image_url=None)
        db.session.add(investigator)
        db.session.commit()
        
        
        
        with self.client as client:
            with client.session_transaction() as sess:
                testuser = User.query.filter(User.username=='testuser').first()
                sess[CURR_USER_KEY] = testuser.id
                investigator = User.query.filter(User.username=='investigator').first()
            resp = client.post('/messages/new', data={'text': 'fake post',
                                                        'user_id': investigator.id}, follow_redirects=True)
            msg = Message.query.one()
            
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            
            # check that the user_id for the new message is corrected to the logged in user 'testuser' instead of the attempted user 'investigator'
            self.assertEqual(msg.user_id, testuser.id)
            self.assertIn('fake post', html)
            