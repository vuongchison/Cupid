from os import path, environ

basedir = path.abspath(path.dirname(__file__))

class Config:
    BASEDIR = basedir
    SECRET_KEY = 'secret key vu0ngch1s0n'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_USERNAME = 'chison1997@gmail.com'
    MAIL_PASSWORD = 'Vu0ng ch1 s0n'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    IMAGES_PATH = ['static/img/avatar', 'static']
    
    @staticmethod
    def init_app(app):
        # print('init_app')
        pass

    @staticmethod
    def init_db(app, db):
        # print('init_db')
        from app.models import Province, Gender, NotificationType
        provincesList = ['An Giang','Bà Rịa - Vũng Tàu','Bạc Liêu','Bắc Kạn','Bắc Giang','Bắc Ninh','Bến Tre','Bình Dương','Bình Định','Bình Phước','Bình Thuận','Cà Mau','Cao Bằng','Cần Thơ','Đà Nẵng','Đắk Lắk','Đắk Nông','Đồng Nai','Đồng Tháp','Điện Biên','Gia Lai','Hà Giang','Hà Nam','Hà Nội','Hà Tĩnh','Hải Dương','Hải Phòng','Hòa Bình','Hậu Giang','Hưng Yên','Thành phố Hồ Chí Minh','Khánh Hòa','Kiên Giang','Kon Tum','Lai Châu','Lào Cai','Lạng Sơn','Lâm Đồng','Long An','Nam Định','Nghệ An','Ninh Bình','Ninh Thuận','Phú Thọ','Phú Yên','Quảng Bình','Quảng Nam','Quảng Ngãi','Quảng Ninh','Quảng Trị','Sóc Trăng','Sơn La','Tây Ninh','Thái Bình','Thái Nguyên','Thanh Hóa','Thừa Thiên - Huế','Tiền Giang','Trà Vinh','Tuyên Quang','Vĩnh Long','Vĩnh Phúc','Yên Bái']
        gendersList = ['Nam', 'Nữ']
        notificationsList = ['admin', 'auth', 'match']
        with app.app_context():
            for province in provincesList:
                p = Province(name=province)
                db.session.add(p)
            for genger in gendersList:
                g = Gender(name=genger)
                db.session.add(g)
            for noti in notificationsList:
                n = NotificationType(name=noti)
                db.session.add(n)
            db.session.commit()



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'data-dev.sqlite')

    @staticmethod
    def init_db(app, db):
        Config.init_db(app, db)
        from app.models import User, Gender, Post
        from datetime import datetime
        with app.app_context():
            print('Initing dev-db......')
            u = User.query.filter_by(email='chison1997@gmail.com').first()
            if u is None:
                u = User(email='chison1997@gmail.com', name='Vương Chí Sơn', password='Son01121997', confirmed_email=True, birthday=datetime(1997, 12, 1), gender_id=1, province_id=1, phone_number='0966772910', about_me='Vương Chí Sơn đẹp trai', height=170, weight=56)
                db.session.add(u)
                db.session.commit()
            u = User.query.filter_by(email='changtrajbjan@gmail.com').first()
            if u is None:
                u = User(email='changtrajbjan@gmail.com', name='Chàng Trai Bí Ẩn', password='Son01121997', confirmed_email=True, birthday=datetime(1997, 12, 1), gender_id=1, province_id=1, phone_number='0966772910', about_me='Vương Chí Sơn đẹp trai', height=175, weight=65)
                db.session.add(u)
                db.session.commit()
            User.generate_fake(20)
            Post.generate_fake(500)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'data.sqlite')

config = {
    'development'   : DevelopmentConfig,
    'production'    : ProductionConfig,
    'testing'       : TestingConfig,

    'default'       : DevelopmentConfig
}