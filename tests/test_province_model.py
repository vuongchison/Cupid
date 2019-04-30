import unittest
from app.models import Province, User
from app import create_app, db
import time
from config import config

class ProvinceModelTestCase(unittest.TestCase):
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
    
    def test_province_exist(self):
        self.assertGreater(len(Province.query.all()), 0)
        p = Province.query.filter_by(name='Hà Nội').first()
        self.assertIsNotNone(p)

    def test_add_province_to_user(self):
        u = User(email='abc@gmail.com', password='123456')
        db.session.add(u)
        p = Province.query.filter_by(name='Hà Nội').first()
        u.province = p
        db.session.add(u)
        self.assertEqual(u.province, p)