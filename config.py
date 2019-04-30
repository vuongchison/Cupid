from os import path, environ

basedir = path.abspath(path.dirname(__file__))

class Config:
    BASEDIR = basedir
    SECRET_KEY = environ.get('SECRET_KEY', 'secret key vu0ngch1s0n') 
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_USERNAME = environ.get('MAIL_USERNAME', 'chison1997@gmail.com')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD', 'Vu0ng ch1 s0n')
    
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    IMAGES_PATH = ['static/img/avatar', 'static/img/post', 'static']
    
    @staticmethod
    def init_app(app):
        # print('init_app')
        pass

    @staticmethod
    def init_db(app, db):
        # print('init_db')
        from app.models import Province, Gender, NotificationType

        provincesList = ['An Giang','Bà Rịa - Vũng Tàu','Bạc Liêu','Bắc Kạn','Bắc Giang','Bắc Ninh','Bến Tre','Bình Dương','Bình Định','Bình Phước','Bình Thuận','Cà Mau','Cao Bằng','Cần Thơ','Đà Nẵng','Đắk Lắk','Đắk Nông','Đồng Nai','Đồng Tháp','Điện Biên','Gia Lai','Hà Giang','Hà Nam','Hà Nội','Hà Tĩnh','Hải Dương','Hải Phòng','Hòa Bình','Hậu Giang','Hưng Yên','Thành phố Hồ Chí Minh','Khánh Hòa','Kiên Giang','Kon Tum','Lai Châu','Lào Cai','Lạng Sơn','Lâm Đồng','Long An','Nam Định','Nghệ An','Ninh Bình','Ninh Thuận','Phú Thọ','Phú Yên','Quảng Bình','Quảng Nam','Quảng Ngãi','Quảng Ninh','Quảng Trị','Sóc Trăng','Sơn La','Tây Ninh','Thái Bình','Thái Nguyên','Thanh Hóa','Thừa Thiên - Huế','Tiền Giang','Trà Vinh','Tuyên Quang','Vĩnh Long','Vĩnh Phúc','Yên Bái']
        coordinatesList = [(10.5149025, 105.1131792), (10.5819798, 107.2899841), (9.2824882, 105.7260685), (22.1321485, 105.8448032), (21.2779313, 106.1938814), (21.1212051, 106.0880245), (10.1245254, 106.4690447), (11.1969829, 106.7080527), (14.1525201, 108.9239618), (11.6790213, 106.797558), (11.101462, 107.9415938), (9.1749605, 105.1960897), (22.6574478, 106.2463873), (10.1131587, 105.6294528), (16.0679814, 108.2119396), (12.8399392, 108.2284947), (12.1288687, 107.5874261), (11.0063212, 107.1921807), (10.5954417, 105.5778479), (21.7210126, 103.0410819), (13.7964067, 108.2608263), (22.8274313, 104.9866145), (20.5269088, 105.9543527), (21.0294498, 105.8544441), (18.3543859, 105.897683), (20.9443681, 106.3780373), (20.858864, 106.6749591), (20.8130014, 105.3452974), (9.7633197, 105.6379524), (20.6490983, 106.0509951), (10.7758439, 106.7017555), (9.3940245, 106.0078954), (9.9776598, 105.2566062), (14.3406675, 107.9807771), (22.3915785, 103.4787316), (22.4997452, 103.9656924), (21.8932309, 106.5884313), (11.6937725, 108.152754), (10.726794, 106.1909011), (20.4230328, 106.1683794), (19.3738868, 104.9233469), (20.2449753, 105.9826291), (11.7449715, 108.8983408), (11.5486226, 109.0281472), (13.2126552, 109.0834225), (17.5462658, 106.2576229), (15.5973344, 107.9758089), (15.1190037, 108.8095598), (21.1718046, 107.2012742), (16.8581352, 106.8588935), (9.5664427, 105.876444), (21.3282643, 103.9005252), (11.365631, 106.1283496), (20.4528848, 106.340023), (21.5545825, 105.7987344), (20.1071694, 105.2124457), (16.3375374, 107.5563708), (10.4176819, 106.1997767), (9.8371629, 106.2394463), (21.8262252, 105.2132832), (10.0937316, 106.0313566), (18.416893, 105.695355), (21.7097865, 104.8872126)]
        
        gendersList = ['Nam', 'Nữ']
        
        notificationsList = ['admin', 'auth', 'match']
        
        with app.app_context():
            i = 0
            for province in provincesList:
                p = Province(name=province)
                p.coordinates = coordinatesList[i]
                i += 1
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
            u1 = User.query.filter_by(email='chison1997@gmail.com').first()
            if u1 is None:
                u1 = User(email='chison1997@gmail.com', name='Vương Chí Sơn', password='Son01121997', confirmed_email=True, birthday=datetime(1997, 12, 1), gender_id=1, province_id=1, phone_number='0966772910', about_me='Vương Chí Sơn đẹp trai', height=170, weight=56)
                db.session.add(u1)
                db.session.commit()
            u2 = User.query.filter_by(email='changtrajbjan@gmail.com').first()
            if u2 is None:
                u2 = User(email='changtrajbjan@gmail.com', name='Chàng Trai Bí Ẩn', password='Son01121997', confirmed_email=True, birthday=datetime(1997, 12, 1), gender_id=1, province_id=1, phone_number='0966772910', about_me='Vương Chí Sơn đẹp trai', height=175, weight=65)
                db.session.add(u2)
                db.session.commit()
            
            u1.follow(u2)
            u2.follow(u1)

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