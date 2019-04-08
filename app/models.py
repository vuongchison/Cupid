from . import db
from . import login_manager
from flask import current_app, url_for
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

class Follow(db.Model):
    __tablrname__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    __tablrname__ = 'matches'
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    name = db.Column(db.String(256), index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed_email = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(256), default='default.png')

    birthday = db.Column(db.DateTime)
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'))
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    phone_number = db.Column(db.String(32))
    about_me = db.Column(db.String(256))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    new_noti = db.Column(db.Integer, default=0)
    
    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    
    match = db.relationship('Match', foreign_keys=[Match.user1_id], backref=db.backref('match', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
        f = Follow(follower=self, followed=self)
        db.session.add(f)

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
        self.active = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def is_active(self):
        """Người dùng có đang online hay không. Thời gian không gửi request quá 5 phút: không online"""
        now = datetime.utcnow()
        return (now - self.active).total_seconds()/60 < 5

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
        if self.is_followed_by(user):
            m1 = Match(user1_id=self.id, user2_id=user.id)
            m2 = Match(user1_id=user.id, user2_id=self.id)
            db.session.add_all([m1, m2])
            self.noti_match(user)
            user.noti_match(self)

        db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            if self.is_followed_by(user):
                m = Match.query.filter( (Match.user1_id == self.id) | (Match.user1_id ==  user.id) ).delete()

            db.session.commit()
    
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id) 

    def is_match_with(self, user):
        return self.match.filter_by(user2_id=user.id).first() is not None

    def noti_match(self, match_with):
        n = Notification(user_id=self.id, type_id=3, image=match_with.avatar, link=url_for('main.user', uuid=match_with.uuid), body='Chúc mừng, bạn và <b>%s</b> đã match với nhau, bạn có thể nhắn tin cho %s ấy.' % (match_with.name, 'anh' if match_with.gender.name == 'Nam' else 'cô'))
        db.session.add(n)
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
    
class NotificationType(db.Model):
    __tablename__ = 'notificationtypes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    note = db.Column(db.Text)

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('notificationtypes.id'))

    image = db.Column(db.Text)
    body = db.Column(db.Text)
    link = db.Column(db.Text)
    
    read = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)
        db.session.add(self)
        db.session.commit()
        self.user.new_noti += 1

    def mark_read(self):
        self.read = True
        self.user.new_noti -= 1
        db.session.add_all([self, self.user])
        db.session.commit()

    
