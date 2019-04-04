import unittest
from app.models import Post, User
from app import create_app, db
import time
from config import config

@unittest.skip
class PostModelTestCase(unittest.TestCase):
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

    def test_create_post(self):
        u = User(email='chison@gmail.com', password='123456')
        db.session.add(u)
        db.session.commit()
        p = Post(body='blabla', author_id=u.id)
        db.session.add(p)
        db.session.commit()
        self.assertIsNotNone(p.id)
        self.assertEqual(p.author_id, u.id)
        self.assertEqual(u.posts[0], p)
    
    