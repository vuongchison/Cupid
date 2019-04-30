import unittest
from app.models import Post, User, Like
from app import create_app, db
import time
from config import config

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
    
    def test_like_post(self):
        u1 = User(email='chison@gmail.com', password='123456')
        u2 = User(email='user2@gmail.com', password='123456')
        db.session.add_all([u1, u2])
        db.session.commit()
        p = Post(body='blabla', author_id=u1.id)
        db.session.add(p)
        db.session.commit()

        # test like post
        u2.like(p)
        self.assertIsNotNone(Like.query.filter_by(user_id=u2.id, post_id=p.id).first())
        self.assertEqual(len(p.likes), 1)
        self.assertEqual(p.likes[0].user, u2)

        # test unlike post
        u2.like(p)
        self.assertIsNone(Like.query.filter_by(user_id=u2.id, post_id=p.id).first())
        self.assertEqual(len(p.likes), 0)

    def test_delete_likes(self):
        u1 = User(email='chison@gmail.com', password='123456')
        u2 = User(email='user2@gmail.com', password='123456')
        db.session.add_all([u1, u2])
        db.session.commit()
        p = Post(body='blabla', author_id=u1.id)
        db.session.add(p)
        db.session.commit()

        u2.like(p)
        p.delete_likes()
        self.assertIsNone(Like.query.filter_by(user_id=u2.id, post_id=p.id).first())
        self.assertEqual(len(p.likes), 0)
