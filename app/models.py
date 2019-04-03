from . import db, gravatar
from . import login_manager
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import tokenHelper 
from uuid import uuid1
import enum
from datetime import datetime

class Gender(db.Model):
    __tablename__ = 'genders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    note = db.Column(db.String(256))

    users = db.relationship('User', backref='gender', lazy='dynamic')

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    name = db.Column(db.String(256), index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed_email = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(256))

    birthday = db.Column(db.DateTime)
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'))
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    phone_number = db.Column(db.String(32))
    about_me = db.Column(db.String(256))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.avatar = gravatar(self.email)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirm_email_token(self, expiration=43200):
        return tokenHelper.gen({'confirm_email': self.id}, expiration)

    def confirm_email(self, token):
        res = tokenHelper.check(token, confirm_email=self.id)
        if not res:
            return False
        
        self.confirmed_email = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_change_email_token(self, new_email, expiration=43200):
        return tokenHelper.gen({'change_email': self.id, 'new_email': new_email}, expiration)

    def change_email(self, token):
        res = tokenHelper.check(token, 'new_email', change_email=self.id)
        if not res:
            return False

        new_email = res['new_email']
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_password_token(self, expiration=43200):
        return tokenHelper.gen({'reset_password': self.id}, expiration)

    @staticmethod
    def reset_password(token, newpassword):
        res = tokenHelper.check(token, 'reset_password')
        if not res:
            return False
            
        u = User.query.get(res['reset_password'])
        if u is None:
            return False

        u.password = newpassword
        db.session.add(u)
        db.session.commit()
        return True 

    @staticmethod
    def generate_fake(count=10):
        import forgery_py
        from random import randint, normalvariate

        gender_count = Gender.query.count()
        provinces_count = Province.query.count()

        i = 0
        while i < count:
            u = User(email=forgery_py.internet.email_address(), name=forgery_py.name.full_name(), password=forgery_py.lorem_ipsum.word(), confirmed_email=True, birthday=forgery_py.date.date(past=True, min_delta=9*365, max_delta=26*365), gender_id=randint(1, gender_count), province_id=randint(1, provinces_count), phone_number=forgery_py.address.phone(), about_me=forgery_py.lorem_ipsum.paragraph(separator='\n', sentences_quantity=randint(1, 6)), weight=int(normalvariate(58, 4)), height= int(normalvariate(164, 7.6)) )
            
            try:
                db.session.add(u)
                i += 1
            except:
                db.session.rollback()
        
        db.session.commit()
                    

    def ping(self):
        print('ping')
        self.active = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %d %s %s %s %s %s %s %s %s>' % (self.id, self.name, self.email, self.birthday, self.gender, self.province, self.phone_number, self.height, self.weight)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=10):
        import forgery_py
        from random import randint, normalvariate

        user_count = User.query.count()

        i = 0
        while i < count:
            p = Post(author_id=randint(1, user_count), body=forgery_py.lorem_ipsum.paragraphs(quantity=randint(1, 5), sentences_quantity=randint(1, 6), separator='\n') )
            
            try:
                db.session.add(p)
                i += 1
            except:
                db.session.rollback()
        
        db.session.commit()


class Province(db.Model):
    __tablename__ = 'provinces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)

    users = db.relationship('User', backref='province', lazy='dynamic')
    
    def __repr__(self):
        return '<Province %d %s>' % (self.id, self.name)
    

