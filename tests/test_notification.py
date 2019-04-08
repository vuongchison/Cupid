import unittest
from app.models import NotificationType, Notification, User
from app import create_app, db
import time
from config import config

class NotificationModelTestCase(unittest.TestCase):
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
    
    def test_noti_type_exist(self):
        self.assertGreater(len(NotificationType.query.all()), 0)
        n = NotificationType.query.filter_by(name='auth').first()
        self.assertIsNotNone(n)

    def test_notification(self):
        u = User(email='vcs@gmail.com')
        db.session.add(u)
        db.session.commit()

        n = Notification(user=u, type_id=1, body='test body noti')
        db.session.add(n)
        db.session.commit()

        self.assertIsNotNone(u.notifications.all())
        self.assertEqual(u.notifications[0], n)
