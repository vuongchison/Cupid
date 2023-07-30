from . import db
from . import login_manager
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from . import tokenHelper 
from uuid import uuid1
import enum
from datetime import datetime
from flask import jsonify
from os import remove
from flask_images import resized_img_src
from geopy import distance
from operator import itemgetter

class Gender(db.Model):
    __tablename__ = 'Gender'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    note = db.Column(db.String(256))

    users = db.relationship('User', backref='gender', lazy='dynamic')

class Follow(db.Model):
    __tablrname__ = 'Follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    __tablrname__ = 'Match'
    user1_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'Message'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    body = db.Column(db.Text)    
    read = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def todict(self):
        return {'id': self.id, 'from': self.sender.uuid, 'to': self.receiver.uuid, 'body': self.body, 'timestamp': self.timestamp.isoformat()}



class LastMessage(db.Model):
    __tablrname__ = 'LastMessage'
    
    id = db.Column(db.Integer, primary_key=True)

    user1_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('Message.id'))

    message = db.relationship('Message')

class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    name = db.Column(db.String(256), index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed_email = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(256), default='default.png')

    birthday = db.Column(db.DateTime)
    gender_id = db.Column(db.Integer, db.ForeignKey('Gender.id'))
    province_id = db.Column(db.Integer, db.ForeignKey('Province.id'))
    phone_number = db.Column(db.String(32))
    about_me = db.Column(db.String(256))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    cell_id = db.Column(db.Integer, db.ForeignKey('Cell.id'))

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

    def todict(self):
        return {'uuid': self.uuid, 'name': self.name, 'avatar': resized_img_src(self.avatar, width=48, height=48, mode='crop'), 'url': url_for('main.user', uuid=self.uuid)}

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password:str) ->bool:
        """Kiểm tra mật khẩu
        - Trả về Tue nếu mật khẩu đúng
        - Trả về False nếu mật khẩu sai"""
        return check_password_hash(self.password_hash, password)

    def generate_confirm_email_token(self, expiration:int=43200) -> str:
        """Sinh token xác nhận email"""
        return tokenHelper.gen({'confirm_email': self.id}, expiration)

    def confirm_email(self, token:str) -> bool:
        """Xác nhận email bằng token
        - Trả về False nếu token không hợp lệ hoặc hết hạn
        - Xác nhận email và trả về True nếu token hợp lệ """

        res = tokenHelper.check(token, confirm_email=self.id)
        if not res:
            return False
        
        self.confirmed_email = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_change_email_token(self, new_email:str, expiration:int=43200) -> str:
        """Sinh token đổi email. new_email: email mới. expriration: thời gian token có hiệu lực, mặc định là 12h
        - Trả về xâu token utf-8"""

        return tokenHelper.gen({'change_email': self.id, 'new_email': new_email}, expiration)

    def change_email(self, token:str) -> bool:
        """Đổi email bằng token
        - Trả về False nếu token không hợp lệ
        - Đổi email và trả về True nếu token hợp lệ"""

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

    def generate_reset_password_token(self, expiration:int=43200) -> str:
        """Sinh token reset mật khẩu. expriration: thời gian token có hiệu lực, mặc định là 12h
        - Trả về xâu token utf-8"""

        return tokenHelper.gen({'reset_password': self.id}, expiration)

    @staticmethod
    def reset_password(token:str, new_password:str) -> bool:
        """Đặt lại mật khẩu bằng token
        - Trả về False nếu token không hợp lệ
        - Đổi mật khẩu người dùng thành new_password và trả về True nếu token hợp lệ"""

        res = tokenHelper.check(token, 'reset_password')
        if not res:
            return False
            
        u = User.query.get(res['reset_password'])
        if u is None:
            return False

        u.password = new_password
        db.session.add(u)
        db.session.commit()
        return True 

    def generate_auth_token(self, expiration:int=43200) -> str:
        """Sinh token dùng cho xác thực api"""

        return tokenHelper.gen({'id': self.id}, expiration=expiration)

    @staticmethod
    def verify_auth_token(token:str) -> 'User':
        """Kiểm tra api token xem có hợp lệ không.
            - Nếu hợp lệ, trả về user tương ứng
            - Nếu không, trả về None"""

        res = tokenHelper.check(token, 'id')
        if not res:
            return None
        return User.query.get(res['id'])
        

    @staticmethod
    def generate_fake(count=10):
        """Sinh người dùng với dữ liệu ngẫu nhiên
        count: số lượng người dùng cần sinh
        Tuổi từ 17-26
        Cân nặng theo phân phối chuẩn, mu=58, sigma=4
        Chiều cao theo phân phối chuẩn, mu=164, sigma=7.6"""

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
        """Cập nhật thời gian hoạt động của user"""

        self.active = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def is_active(self):
        """Người dùng có đang online hay không. Thời gian không gửi request quá 5 phút: không online"""
        now = datetime.utcnow()
        return (now - self.active).total_seconds()/60 < 5


    def follow(self, user:'User'):
        """Theo dõi user"""

        #Nếu chưa theo dõi user
        if not self.is_following(user):
            #Theo dõi
            f = Follow(follower=self, followed=user)
            db.session.add(f)
        
        #Nếu 2 người theo dõi nhau
        if self.is_followed_by(user):
            #2 người match với nhau
            m1 = Match(user1_id=self.id, user2_id=user.id)
            m2 = Match(user1_id=user.id, user2_id=self.id)
            db.session.add_all([m1, m2])
            #Thông báo 2 người đã được match
            self.notify_match(match_with=user)
            user.notify_match(match_with=self)

        db.session.commit()

    def unfollow(self, user:'User'):
        """Hủy theo dõi user"""

        f = self.followed.filter_by(followed_id=user.id).first()
        #Nếu đang theo dõi user
        if f:
            #Hủy theo dõi
            db.session.delete(f)
            #Nếu 2 người match với nhau
            if self.is_followed_by(user):
                #Xóa match
                m = Match.query.filter( (Match.user1_id == self.id) | (Match.user1_id ==  user.id) ).delete()

            db.session.commit()
    
    def is_following(self, user:'User') -> bool:
        """Có đang theo dõi user hay không"""
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user:'User') -> bool:
        """Có đang được user theo dõi hay không"""
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self) -> 'query':
        """"Trả về câu truy vấn các post của những người mà người dùng theo dõi"""
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id) 

    def get_followed_posts(self, count, time=None):
        if time is None:
            time = datetime.utcnow()
        bucket = Post.get_bucket(time)
        listPost = []
        for b in range(bucket, -1, -1):
            listPost += Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Post.bucket==b,Post.created < time, Follow.follower_id == self.id).order_by(Post.created.desc()).all()
            if len(listPost) >= count:
                break
        return listPost[:count]


    def is_match_with(self, user:'User') -> bool:
        """2 người có match với nhau hay không"""
        return self.match.filter_by(user2_id=user.id).first() is not None

    def notify(self, type_id:int, image:str=None, link:str=None, body:str=None):
        """Gửi thông báo đến người dùng.
        type_id: loại thông báo. 1: admin, 2: auth, 3: match, 4: like, 5: comment
        image: đường dẫn đến hình ảnh minh họa thông báo
        link: đường dẫn khi người dùng click vào thông báo
        body: nội dung thông báo, đoạn html"""

        n = Notification(user_id=self.id, type_id=type_id, image=image, link=link, body=body)
        self.new_noti += 1
        db.session.add(n)
        db.session.commit()

    def notify_match(self, match_with:'User'):
        """Thông báo người dùng match với 1 người dùng"""

        body = 'Chúc mừng, bạn và <b>%s</b> đã match với nhau, bạn có thể nhắn tin cho %s ấy.' % (match_with.name or 'người ấy', 'bạn' if match_with.gender is None else 'anh' if match_with.gender.name == 'Nam' else 'cô')
        self.notify(type_id=3, image=match_with.avatar, link=url_for('main.user', uuid=match_with.uuid), body=body)
    
    def notify_like_post(self, user:'User', post:'Post'):
        """Thông báo đến người dùng có 1 người đã like post"""

        body = '<b>%s</b> đã thích bài đăng của bạn.' % (user.name)
        self.notify(type_id=4, image=user.avatar, link=url_for('main.post', uuid=post.uuid), body=body)

    def notify_comment_post(self, user, post):
        """Thông báo đến người dùng có 1 người đã bình luận post"""
        body = '<b>%s</b> đã bình luận vào bài đăng của bạn.' % (user.name)
        self.notify(type_id=5, image=user.avatar, link=url_for('main.post', uuid=post.uuid), body=body)

    def notify_first_login(self):
        """Gửi thông báo khi người dùng login lần đầu tiên"""

        self.notify(1, image='admin_avatar.png', link=url_for('main.edit_info'), body='Hãy cập nhật hồ sơ của bạn để mọi người biết về bạn nhiều hơn!')

    def message(self, receiver:'User', body:str)->'Message':
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
    def last_messages(self) -> 'query':
        """Các tin nhắn cuối cùng với mọi người. Kết quả trả về dưới dạng 1 câu truy vấn."""
        return LastMessage.query.filter_by(user1_id=self.id).join(Message, Message.id == LastMessage.message_id)

    def get_latest_messages(self, user:'User') -> 'query':
        """Trả về câu truy vấn lấy các tin nhắn với user, sắp xếp từ tin nhắn mới đến cũ."""
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
    def coordinates(self, coordinates:'(latitude, longitude)'):
        """Thiết đặt tọa độ địa lý cho user.
        - coordinates: 1 bộ gồm kinh độ và vĩ độ (latitude, longitude)"""
        self.latitude, self.longitude = coordinates

        Cell.add_user(self)


    def distance(self, user:'User')->float:
        """Trả về khoảng cách giữa 2 người (tính bằng km)"""
        return distance.distance(self.coordinates, user.coordinates).km

    def calculate_distances(self):
        """Tính toán khoảng cách của người dùng đến tất cả người dùng khác giới"""
        #Tìm tất cả người dùng khác giới
        for u in User.query.filter(User.gender_id != self.gender_id).all():
            #Tính khoảng cách giữa 2 người
            d = self.distance(u)

            if (u.id < self.id):
                user1, user2 = u, self
            else:
                user2, user1 = u, self
            #Tìm bản ghi khỏang cách giữa 2 người trong Distance
            dis = Distance.query.filter_by(user1_id=user1.id, user2_id=user2.id).first()
            #Nếu đã có
            if dis:
                #Cập nhật lạu khoảng cách và timestamp
                dis.d = d
                dis.timestamp = datetime.utcnow()
            #Chưa có
            else:
                #Thêm bản ghi mới
                dis = Distance(user1_id=user1.id, user2_id=user2.id, distance=d)
                db.session.add(dis)
        
        db.session.commit()

    def get_near_people(self, d:'km', count:int):
        userCell = self.cell

        allCellD = CellDistance.query.filter((CellDistance.cell1_id==userCell.id) | (CellDistance.cell2_id==userCell.id), CellDistance.distance >= (int(d)//111-1)*157, CellDistance.distance <= (int(d)//111+1)*157).order_by(CellDistance.distance.asc()).all()
        allCell = []
        if d <= 157:
            allCell.append(userCell)
    
        for cellD in allCellD:
            if cellD.cell1_id == userCell.id:
                allCell.append(Cell.query.get(cellD.cell2_id))
            else:
                allCell.append(Cell.query.get(cellD.cell1_id))
        
        if len(allCell) == 0:
            return []

        peopleList=[]
        
        for c in allCell:
            for u in c.users:
                if u != self:
                    dis = self.distance(u)
                    if dis >= d:
                        peopleList.append((u, dis))
            if len(peopleList) >= count:
                        break
        
        if len(peopleList) < count:
            peopleList+=self.get_near_people(d + 111, count - len(peopleList))

        return sorted(peopleList, key=itemgetter(1))[:count]
        


    def like(self, post:'Post'):
        """Thích 1 bài post"""
        l = Like.query.filter_by(user_id=self.id, post_id=post.id).first()
        #Nếu đã like post
        if l is not None:
            #unlike
            post.count_likes -= 1
            db.session.delete(l)
        #Chưa like post
        else:
            #Like post
            post.count_likes += 1
            l = Like(user_id=self.id, post_id=post.id)
            db.session.add(l)

            # Gửi thông báo đến chủ bài post
            if self != post.author:
                post.author.notify_like_post(user=self, post=post)
        db.session.commit()
    
    def is_like(self, post:'Post') -> bool:
        """Người dùng đã like post hay chưa"""
        return Like.query.filter_by(user_id=self.id, post_id=post.id).first() is not None


    def comment(self, post:'Post', body:str):
        """Bình luận vào bài post với nội dung body"""
        c = Comment(user_id=self.id, post_id=post.id, body=body)
        post.count_comments += 1
        db.session.add(c)
        db.session.commit()

        # Gửi thông báo đến chủ bài post
        if self != post.author:
            post.author.notify_comment_post(user=self, post=post)
        return c

    def view(self, user:'User'):
        """Đánh dấu đã ghe thăm người dùng user"""
        v = View(viewer_id=self.id, user_id=user.id)
        db.session.add(v)
        db.session.commit()

    def __repr__(self):
        return '<User %d %s %s %s %s %s %s %s %s>' % (self.id, self.name, self.email, self.birthday, self.gender, self.province, self.phone_number, self.height, self.weight)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    bucket = db.Column(db.Integer, default=lambda : Post.get_bucket(datetime.now()), index=True)
    images = db.relationship('Image', backref='post', lazy='dynamic')

    likes = db.relationship('Like')
    count_likes = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment')
    count_comments = db.Column(db.Integer, default=0)

    @staticmethod
    def generate_fake(count=10):
        """Sinh dữ liệu post ngẫu nhiên"""

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

    def todict(self):
        return {'uuid': self.uuid, 'author': self.author.todict(), 'body': self.body, 'created': self.created.isoformat(), 'images': [ url_for('images.crop', filename=i.uuid + '.png', width=1000, height=1000, quality=90) for i in self.images], 'count_likes': self.count_likes, 'count_comments': self.count_comments}

    def get_latest_comments(self):
        """Trả về câu truy vấn lấy tất cả comment của post, sắp xếp từ mới đến cũ."""
        return Comment.query.filter_by(post_id=self.id).order_by(Comment.timestamp.desc())

    def delete_images(self):
        """Xóa tất cả ảnh của post"""

        for i in self.images:
            remove('app/static/img/post/' + i.uuid + '.png')
            db.session.delete(i)
        db.session.commit()

    def delete_likes(self):
        """Xóa tất cả like của post"""

        Like.query.filter_by(post_id=self.id).delete()
        self.count_likes = 0
        db.session.commit()

    def delete_comments(self):
        """Xóa tất cả comment của post"""

        Comment.query.filter_by(post_id=self.id).delete()
        self.count_comments = 0
        db.session.commit()

    def delete(self):
        """Xóa post"""

        self.delete_images()
        self.delete_comments()
        self.delete_likes()
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def update_bucket():
        for p in Post.query.all():
            p.bucket = Post.get_bucket(p.created)
        db.session.commit()

    @staticmethod
    def get_bucket(timestamp):
        #Gom các post trong 3 ngày thành 1 bucket
        return int((timestamp - datetime(2019, 6, 1, 0, 0, 0)).total_seconds() // (3*24*60*60))

class Province(db.Model):
    __tablename__ = 'Province'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    users = db.relationship(User, backref='province', lazy='dynamic')
    
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
    __tablename__ = 'NotificationType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    note = db.Column(db.Text)

class Notification(db.Model):
    __tablename__ = 'Notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('NotificationType.id'))
    type_notification = db.relationship('NotificationType')

    image = db.Column(db.Text)
    body = db.Column(db.Text)
    link = db.Column(db.Text)
    
    read = db.Column(db.Boolean, default=False, index=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def mark_read(self):
        self.read = True
        db.session.commit()

class PostNoti(db.Model):
    __tablename__ = 'PostNoti'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ReadPostNoti(db.Model):
    __tablename__ = 'ReadPostNoti'

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    postnoti_id = db.Column(db.Integer, db.ForeignKey('PostNoti.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)     

class Image(db.Model):
    __tablename__ = 'Image'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True, index=True, default=lambda : uuid1().hex)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), index=True)


class Like(db.Model):
    __tablename__ = 'Like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), index=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    post = db.relationship('Post')

class Comment(db.Model):
    __tablename__ = 'Comment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), index=True)

    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    post = db.relationship('Post')

    def todict(self):
        return {'id': self.id, 'user': self.user.todict(), 'body': self.body, 'timestamp': self.timestamp.isoformat()}

class Distance(db.Model):
    __tablename__ = 'Distance'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    distance = db.Column(db.Float, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())


class View(db.Model):
    __tablename__ = 'View'

    id = db.Column(db.Integer, primary_key=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

class Cell(db.Model):
    __tablename__ = 'Cell'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    count = db.Column(db.Integer, default=0)

    users = db.relationship(User, backref='cell', lazy='dynamic')

    @property
    def coordinates(self):
        return (self.latitude, self.longitude)

    def calculate_distances(self):
        allCell = Cell.query.filter(Cell.id != self.id).all()
        for cell in allCell:
            if cell.id < self.id:
                cd = CellDistance(cell1_id=cell.id, cell2_id=self.id, distance=distance.distance(self.coordinates, cell.coordinates).km)
                db.session.add(cd)
        db.session.commit()

    @staticmethod
    def update_count():
        for c in Cell.query.all():
            c.count = c.users.count()
        db.session.commit()

    @staticmethod
    def add_user(user):
        lat, long = user.coordinates
        lat = int(lat)
        long = int(long)
        c = Cell.query.filter_by(latitude=lat, longitude=long).first()
        if c is None:
            c = Cell(latitude=lat, longitude=long, count=0)
            c.calculate_distances()
            db.session.add(c)

        uc = user.cell
        if uc is not None:
            if uc.id != c.id:
                uc.count -= 1
                user.cell_id = c.id
                c.count += 1
        else:
            user.cell_id = c.id
        db.session.commit()

# class UserCell(db.Model):
#     __tablename__ = 'UserCell'

#     user_id = db.Column(db.Integer, db.ForeignKey('User.id'), index=True, primary_key=True)
#     cell_id = db.Column(db.Integer, db.ForeignKey('Cell.id'), index=True, primary_key=True)

#     cell = db.relationship('Cell')

class CellDistance(db.Model):
    __tablename__ = 'CellDistance'

    cell1_id = db.Column(db.Integer, db.ForeignKey('Cell.id'), primary_key=True)
    cell2_id = db.Column(db.Integer, db.ForeignKey('Cell.id'), primary_key=True)
    distance = db.Column(db.Float, index=True)