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
from flask import jsonify
from os import remove
from flask_images import resized_img_src

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

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    body = db.Column(db.Text)    
    read = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def todict(self):
        return {'id': self.id, 'from': self.sender.uuid, 'to': self.receiver.uuid, 'body': self.body, 'timestamp': self.timestamp.isoformat()}



class LastMessage(db.Model):
    __tablrname__ = 'lastmessages'
    
    id = db.Column(db.Integer, primary_key=True)

    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))

    message = db.relationship('Message')

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
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    new_noti = db.Column(db.Integer, default=0)
    
    message_s = db.relationship('Message', foreign_keys=[Message.sender_id], backref=db.backref('sender', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    message_r = db.relationship('Message', foreign_keys=[Message.receiver_id], backref=db.backref('receiver', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    new_message = db.Column(db.Integer, default=0)


    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    
    match = db.relationship('Match', foreign_keys=[Match.user1_id], backref=db.backref('match', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    # def __init__(self, **kwargs):
    #     super(User, self).__init__(**kwargs)
        
    #     f = Follow(follower=self, followed=self)
    #     db.session.add(f)

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

    def generate_auth_token(self, expiration=43200):
        """Sinh token dùng cho xác thực api"""
        return tokenHelper.gen({'id': self.id}, expiration=expiration)

    @staticmethod
    def verify_auth_token(token):
        """Kiểm tra token xem có hợp lệ không.
            - Nếu hợp lệ, trả về user tương ứng
            - Nếu không, trả về None"""

        res = tokenHelper.check(token, 'id')
        if not res:
            return None
        return User.query.get(res['id'])
        

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
            self.notify_match(match_with=user)
            user.notify_match(match_with=self)

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

    def notify(self, type_id, image=None, link=None, body=None):
        n = Notification(user_id=self.id, type_id=type_id, image=image, link=link, body=body)
        self.new_noti += 1
        db.session.add(n)
        db.session.commit()

    def notify_match(self, match_with):
        body = 'Chúc mừng, bạn và <b>%s</b> đã match với nhau, bạn có thể nhắn tin cho %s ấy.' % (match_with.name or 'người ấy', 'bạn' if match_with.gender is None else 'anh' if match_with.gender.name == 'Nam' else 'cô')
        self.notify(type_id=3, image=match_with.avatar, link=url_for('main.user', uuid=match_with.uuid), body=body)
    
    def notify_like_post(self, user, post):
        body = '<b>%s</b> đã thích bài đăng của bạn.' % (user.name)
        self.notify(type_id=4, image=user.avatar, link=url_for('main.post', uuid=post.uuid), body=body)
        print('notify_like_post')

    def notify_comment_post(self, user, post):
        body = '<b>%s</b> đã bình luận vào bài đăng của bạn.' % (user.name)
        self.notify(type_id=5, image=user.avatar, link=url_for('main.post', uuid=post.uuid), body=body)
        print('notify_comment_post')


    def message(self, receiver: 'User', body)->'Message':
        """Gửi tin nhắn. Trả về đối tượng Message."""
        m = Message(sender_id=self.id, receiver_id=receiver.id, body=body)
        db.session.add(m)
        receiver.new_message += 1
        
        lm1 = LastMessage.query.filter( LastMessage.user1_id == self.id, LastMessage.user2_id == receiver.id ).first()
        if lm1 is None:
            lm3 = LastMessage(user1_id=self.id, user2_id=receiver.id, message=m)
            lm2 = LastMessage(user2_id=self.id, user1_id=receiver.id, message=m)
            db.session.add_all([lm3, lm2])
        else:
            lm1.message = m
            lm2 = LastMessage.query.filter(  LastMessage.user2_id == self.id, LastMessage.user1_id == receiver.id ).first()
            lm2.message = m
        
        db.session.commit()
        return m

    @property
    def last_messages(self):
        """Các tin nhắn cuối cùng với mọi người. Kết quả tả về dưới dạng 1 câuu truy vấn."""
        return LastMessage.query.filter_by(user1_id=self.id).join(Message, Message.id == LastMessage.message_id)

    def get_latest_messages(self, user):
        """Trả về câu truy vấn lấy các tin nhắn với user, xắp sếp từ tin nhắn mới đến cũ."""
        return Message.query.filter( (Message.sender_id == self.id) | (Message.receiver_id == self.id) ).order_by(Message.timestamp.desc())

    @property
    def coordinates(self)->'(latitude, longitude)':
        """Trả về tọa độ địa lý của user dưới dạng 1 bộ: (latitude, longitude).
            - Nếu không biết được vị trí chính xác, trả về tọa độ của tỉnh/ thành của user
            - Nếu không biết tỉnh/ thành của user, trả về None"""
        if self.latitude is not None:
            return (self.latitude, self.longitude)
        elif self.province_id is not None:
            return self.province.coordinates
        else:
            return None

    @coordinates.setter
    def coordinates(self, coordinates: '(latitude, longitude)'):
        """Thiết đặt tọa độ địa lý cho user.
        - coordinates: 1 bộ gồm kinh độ và vĩ độ (latitude, longitude)"""
        self.latitude, self.longitude = coordinates

    def like(self, post):
        l = Like.query.filter_by(user_id=self.id, post_id=post.id).first()
        if l is not None:
            post.count_likes -= 1
            db.session.delete(l)
        else:
            post.count_likes += 1
            l = Like(user_id=self.id, post_id=post.id)
            db.session.add(l)

            # Gửi thông báo đến chủ bài post
            if self != post.author:
                post.author.notify_like_post(user=self, post=post)
        db.session.commit()
    
    def is_like(self, post):
        return Like.query.filter_by(user_id=self.id, post_id=post.id).first() is not None


    def comment(self, post, body):
        """Bình luận vào bài post với nội dung body."""
        c = Comment(user_id=self.id, post_id=post.id, body=body)
        post.count_comments += 1
        db.session.add(c)
        db.session.commit()

        # gửi thông báo đến chủ bài post
        if self != post.author:
            post.author.notify_comment_post(user=self, post=post)
        return c

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
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    images = db.relationship('Image', backref='post', lazy='dynamic')

    likes = db.relationship('Like')
    count_likes = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment')
    count_comments = db.Column(db.Integer, default=0)

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

    def get_latest_comments(self):
        """Trả về câu truy vấn lấy tất cả comment của post, sắp xếp từ mới đến cũ."""
        return Comment.query.filter_by(post_id=self.id).order_by(Comment.timestamp.desc())

    def delete_images(self):
        for i in self.images:
            remove('app/static/img/post/' + i.uuid + '.png')
            db.session.delete(i)
        db.session.commit()

    def delete_likes(self):
        Like.query.filter_by(post_id=self.id).delete()
        self.count_likes = 0
        db.session.commit()

    def delete_comments(self):
        Comment.query.filter_by(post_id=self.id).delete()
        self.count_comments = 0
        db.session.commit()

class Province(db.Model):
    __tablename__ = 'provinces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    users = db.relationship('User', backref='province', lazy='dynamic')
    
    @property
    def coordinates(self)->'(latitude, longitude)':
        """Trả về tọa độ địa lý của tỉnh/ thành dưới dạng 1 bộ: (latitude, longitude)."""
    
        return (self.latitude, self.longitude)

    @coordinates.setter
    def coordinates(self, coordinates: '(latitude, longitude)'):
        """Thiết đặt tọa độ địa lý.
        - coordinates: 1 bộ gồm kinh độ và vĩ độ (latitude, longitude)"""
        self.latitude, self.longitude = coordinates

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
    
    read = db.Column(db.Boolean, default=False, index=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # def __init__(self, **kwargs):
    #     super(Notification, self).__init__(**kwargs)
    #     db.session.add(self)
    #     db.session.commit()
    #     self.user.new_noti += 1

    def mark_read(self):
        self.read = True
        db.session.commit()

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    post = db.relationship('Post')

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)

    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    post = db.relationship('Post')

    def todict(self):
        return {'id': self.id, 'user': {'uuid': self.user.uuid, 'name': self.user.name, 'avatar': resized_img_src(self.user.avatar, width=48, height=48, mode='crop'), 'url': url_for('main.user', uuid=self.user.uuid)}, 'body': self.body, 'timestamp': self.timestamp.isoformat()}