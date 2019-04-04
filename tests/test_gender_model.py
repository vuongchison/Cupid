import unittest
from app.models import Gender, User
from app import create_app, db
import time
from config import config

@unittest.skip
class GenderModelTestCase(unittest.TestCase):
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
    
    def test_gender_exist(self):
        self.assertGreater(len(Gender.query.all()), 0)
        g = Gender.query.filter_by(name='Nam').first()
        self.assertIsNotNone(g)

    def test_add_gender_to_user(self):
        u = User(email='abc@gmail.com', password='123456')
        db.session.add(u)
        g = Gender.query.filter_by(name='Nam').first()
        u.gender_id = g.id
        db.session.add(u)
        self.assertEqual(u.gender, g)