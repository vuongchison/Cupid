from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional
from app.models import Gender, User, Post, Province


class InformationForm(FlaskForm):
    birthday = DateField('Ngày sinh', format='%d/%m/%Y', validators=[Optional()])
    gender = SelectField('Giới tính', coerce=int)
    province = SelectField('Tỉnh thành', coerce=int)
    phone_number = StringField('Số điện thoại')
    about_me = TextAreaField('Giới thiệu')
    height = SelectField('Chiều cao (cm)', coerce=int)
    weight = SelectField('Cân nặng (kg)', coerce=int)
    submit = SubmitField('Đồng ý')

    def __init__(self, user: User, *args, **kwargs):
        super(InformationForm, self).__init__(*args, **kwargs)
        
        self.gender.choices = [(0, "--Không hiển thị--")] + [(gender.id, gender.name) for gender in Gender.query.all() ]
        self.province.choices = [(0, "--Không hiển thị--")] + [(province.id, province.name) for province in Province.query.all()]
        self.height.choices = [(0, "--Không hiển thị--")] + [(v, v) for v in range(220, 119, -1)]
        self.weight.choices = [(0, "--Không hiển thị--")] + [(v, v) for v in range(100, 29, -1)]
        
class PostForm(FlaskForm):
    body = TextAreaField('Bài đăng mới', validators=[DataRequired()])
    image = FileField('Chọn ảnh')
    submit = SubmitField('Đăng')

class EditPostForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Lưu thay đổi')


class ChangeAvatarForm(FlaskForm):
    newavatar = FileField('Chọn avatar mới')
    submit = SubmitField('Tải lên')
    cancel = SubmitField('Hủy bỏ')