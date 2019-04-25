import unittest
from app.models import  Message, User
from app import create_app, db
import time
from config import config

class MessageModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        config['testing'].init_db(self.app, db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_message(self):
        u1 = User(email='vcs1@gmail.com')
        u2 = User(email='vcs2@gmail.com')

        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertEqual(u1.message_s.count(), 0)
        self.assertEqual(u1.message_r.count(), 0)
        self.assertEqual(u2.message_r.count(), 0)
        self.assertEqual(u2.message_s.count(), 0)

        u1.message(u2, 'test')

        self.assertIsNotNone(Message.query.all())
        self.assertEqual(Message.query.count(), 1)

        m = Message.query.all()[0]
        self.assertEqual(m.sender_id, u1.id)
        self.assertEqual(m.sender, u1)
        self.assertEqual(m.receiver_id, u2.id)
        self.assertEqual(m.receiver, u2)
        self.assertEqual(m.body, 'test')
        self.assertEqual(u2.new_message, 1)

        self.assertEqual(m, u1.message_s[0])
        self.assertEqual(m, u2.message_r[0])

        self.assertEqual(u1.message_s.count(), 1)
        self.assertEqual(u1.message_r.count(), 0)
        self.assertEqual(u2.message_r.count(), 1)
        self.assertEqual(u2.message_s.count(), 0)

    def test_last_messages(self):
        u1 = User(email='vcs1@gmail.com')
        u2 = User(email='vcs2@gmail.com')

        db.session.add_all([u1, u2])
        db.session.commit()

        u1.message(u2, 'test')
        self.assertEqual(u1.last_messages.count(), 1)
        self.assertEqual(u2.last_messages.count(), 1)

        u2.message(u1, 'test2')
        self.assertEqual(u1.last_messages.count(), 1)
        self.assertEqual(u2.last_messages.count(), 1)