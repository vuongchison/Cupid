import unittest
from app.models import User, Follow
from app import create_app, db
import time
from config import config

class UserModelTestCase(unittest.TestCase):
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

    
    def test_create_user(self):
        u = User(email='example@gmail.com', name='Vương Chí Sơn', password='nulo')
        db.session.add(u)
        db.session.commit()
        u1 = User.query.filter_by(email='example@gmail.com').first()
        self.assertEqual(u, u1)

    def test_password(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

        with self.assertRaises(AttributeError):
            u.password

        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_confirm_email(self):
        u = User(email='example@gmail.com')
        db.session.add(u)
        db.session.commit()
        
        #test User.confirmed_email default value
        u = User.query.filter_by(email='example@gmail.com').first()
        self.assertFalse(u.confirmed_email)
        
        #test token confirm email
        token = u.generate_confirm_email_token()
        u.confirm_email(token)
        self.assertTrue(u.confirmed_email)

        u2 = User(email='example2@gmail.com')
        db.session.add(u2)
        db.session.commit()
        u2.confirm_email(token)
        self.assertFalse(u2.confirmed_email)

        #test expiration token
        token2 = u2.generate_confirm_email_token(expiration=1)
        time.sleep(2)
        u2.confirm_email(token2)
        self.assertFalse(u2.confirmed_email)
    
    def test_uuid(self):
        u = User(email='chison@gmail.com')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.uuid)

        u2 = User(email='chison2@gmail.com')
        db.session.add(u)
        db.session.commit()
        self.assertNotEqual(u.uuid, u2.uuid)
    
    def test_reset_password(self):
        u1 = User(email= 'u1@gmail.com', password='Nulo123456')
        u2 = User(email= 'u2@gmail.com', password='Nulo123456')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token1 = u1.generate_reset_password_token()
        token2 = u2.generate_reset_password_token()

        #test generate token success
        self.assertIsNotNone(token1)
        self.assertIsNotNone(token2)

        #test token difference
        self.assertNotEqual(token1, token2)

        #test valid token
        self.assertTrue(User.reset_password(token1, newpassword='Newpass123456'))
        self.assertTrue(u1.verify_password('Newpass123456'))

        #test not valid token
        self.assertFalse(User.reset_password(token2 + '123', newpassword='Newpass123456'))
        self.assertTrue(u2.verify_password('Nulo123456'))

        #test expiration token
        token2 = u2.generate_reset_password_token(expiration=1)
        time.sleep(2)
        self.assertFalse(User.reset_password(token2, newpassword='Newpass123456'))
        self.assertTrue(u2.verify_password('Nulo123456'))

    def test_change_email(self):
        u1 = User(email= 'u1@gmail.com')
        u2 = User(email= 'u2@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token1 = u1.generate_change_email_token('newu1@gmail.com')
        token2 = u2.generate_change_email_token('newu2@gmail.com')

        #test generate token success
        self.assertIsNotNone(token1)
        self.assertIsNotNone(token2)

        #test token difference
        self.assertNotEqual(token1, token2)

        #test valid token
        self.assertTrue(u1.change_email(token1))
        self.assertEqual(u1.email, 'newu1@gmail.com')

        #test not valid token
        self.assertFalse(u2.change_email(token2 + '123'))
        self.assertNotEqual(u2.email, 'newu2@gmail.com')

        #test expiration token
        token2 = u2.generate_change_email_token(new_email='newu2@gmail.com', expiration=1)
        time.sleep(2)
        self.assertFalse(u2.change_email(token2))

    def test_follow(self):
        u1 = User(email= 'u1@gmail.com')
        u2 = User(email= 'u2@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        #test u1 is follwing u1
        self.assertTrue(u1.is_following(u1))

        #test u2 is not following u1
        self.assertFalse(u2.is_following(u1))
        self.assertFalse(u1.is_followed_by(u2))

        #test u1 is not following u2
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_followed_by(u1))

        #test u1 is following u2
        u1.follow(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))

    def test_match(self):
        u1 = User(email= 'u1@gmail.com')
        u2 = User(email= 'u2@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1.follow(u2)
        u2.follow(u1)

        #test match
        self.assertTrue(u1.is_match_with(u2))
        self.assertTrue(u2.is_match_with(u1))

        #test unmatch
        u1.unfollow(u2)
        self.assertFalse(u1.is_match_with(u2))
        self.assertFalse(u2.is_match_with(u1))

    def test_active(self):
        u1 = User(email= 'u1@gmail.com')
        db.session.add(u1)
        db.session.commit()

        self.assertTrue(u1.is_active())