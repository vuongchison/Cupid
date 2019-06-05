from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from ..models import User

#Các ký tự hợp lệ của tên người dùng
nameRegex = '^[a-zA-Z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\\s]+$'

#Mật khẩu phải từ 8-32 ký tự, gồm cả chữ hoa, chữ thường và số
passwordValidate = [Length(8, 32, message='Mật khẩu dài từ 8 đến 32 ký tự'), Regexp('[A-Za-z0-9 !"#$%&\'()*+,\-./:;<=>?@[\\]^_`{|}~]', message='Mật khẩu chứa ký tự không hợp lệ'), Regexp('.*[0-9].*', message='Mật khẩu phải chứa ít nhất 1 chữ số'), Regexp('.*[a-z].*', message='Mật khẩu phải chứa ít nhất 1 chữ thường'), Regexp('.*[A-Z].*', message='Mật khẩu phải chứa ít nhất 1 chữ hoa')]

class LoginForm(FlaskForm):
    """Đăng nhập"""

    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegistrationForm(FlaskForm):
    """Đăng ký"""

    email= StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    name = StringField('Họ và tên', validators=[DataRequired(), Length(1, 256), Regexp(nameRegex, 0, message='Họ và tên thật, chỉ chứa ký tự và dấu cách')])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), *passwordValidate])
    password2 = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp.')])
    submit = SubmitField('Đăng ký')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email đã được sử dụng.')
    
class ChangePasswordForm(FlaskForm):
    """Đổi mật khẩu"""

    oldpassword = PasswordField('Mật khẩu', validators=[DataRequired()]) 
    newpassword = PasswordField('Mật khẩu mới', validators=[DataRequired(), *passwordValidate])
    newpassword2 = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('newpassword', message='Mật khẩu không khớp.')])
    submit = SubmitField('Đổi mật khẩu')

    def __init__(self, user: User, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_oldpassword(self, password):
        if not self.user.verify_password(password.data):
            raise ValidationError('Mật khẩu sai')

class ChangeEmailForm(FlaskForm):
    """Đổi email"""

    newemail = StringField('Email mới', validators=[DataRequired(), Length(1, 128), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đổi email')

    def __init__(self, user: User, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_oldpassword(self, password):
        if not self.user.verify_password(password.data):
            raise ValidationError('Mật khẩu sai')

    def validate_email(self, email):
        if self.user.email == email.data:
            raise ValidationError('Email chưa được thay đổi.')
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email đã được sử dụng.')
        

class ResetPasswordRequestForm(FlaskForm):
    """Gửi yêu cầu đặt lại mật khẩu"""

    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    submit = SubmitField('Đặt lại mật khẩu')

    def validate_email(self, email):
        if not User.query.filter_by(email=email.data).first():
            raise ValidationError('Email không tồn tại.')


class ResetPasswordForm(FlaskForm):
    """Đặt lại mật khẩu"""

    newpassword = PasswordField('Mật khẩu mới', validators=[DataRequired(), *passwordValidate])
    newpassword2 = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('newpassword', message='Mật khẩu không khớp.')])
    submit = SubmitField('Đặt lại mật khẩu')



