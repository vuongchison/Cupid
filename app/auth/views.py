from flask import render_template, url_for, request, redirect, flash
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm, ChangeEmailForm
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        else:
            flash('Email hoặc mật khẩu không hợp lệ.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email=form.email.data, name=form.name.data, password=form.password.data)
        db.session.add(u)
        db.session.commit()
        flash('Đăng ký thành công, vui lòng kiểm tra email và xác nhận.')
        token = u.generate_confirm_email_token()
        send_email(to=u.email, subject='Xác nhận email', template='auth/email/confirm_email', user=u, token=token)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm-email/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed_email:
        return redirect('main.index')
    
    if current_user.confirm_email(token):
        flash('Xác nhận email thành công.')
    else:
        flash('Link xác nhận không chính xác hoặc đã hết hạn.')
    
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirm_email_token()
    send_email(to=current_user.email, subject='Xác nhận email', template='auth/email/confirm_email', user=current_user, token=token)
    flash('Email xác nhận đã được gửi đến mail cua bạn.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed_email and request.endpoint and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
    
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed_email:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(current_user)
    if form.validate_on_submit():
        current_user.password = form.newpassword.data
        db.session.add(current_user)
        db.session.commit()
        flash('Mật khẩu thay đổi thành công')
        return redirect(url_for('main.user_homepage'))
    return render_template('auth/change_password.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        token = u.generate_reset_password_token()
        send_email('Đặt lại mật khẩu', u.email, 'auth/email/reset_password', token=token, user=u)
        flash('Email xác nhận đã được gửi đến email của bạn.')
        return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.newpassword.data):
            flash('Đặt lại mật khẩu thành công.')
            return redirect(url_for('auth.login'))
        else:
            flash('Link đặt lại mật khẩu không chính xác hoặc hết hạn, vui lòng thử lại.')
            return redirect('auth.reset_password_request')
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm(current_user)
    if form.validate_on_submit():
        new_email = form.newemail.data
        token = current_user.generate_change_email_token(new_email=new_email)
        send_email('Thay đổi email', new_email, 'auth/email/change_email', token=token, user=current_user)
        flash('Email xác nhận đã được gửi tới %s.' % new_email)
        return redirect(url_for('auth.change_email_request'))
    return render_template('auth/change_email.html', form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Đổi email thành công, xin vui lòng đăng nhập lại.')
        logout_user()
        return redirect(url_for('auth.login'))
    else:
        flash('Link thay đổi email không chính xác hoặc hết hạn, vui lòng thử lại.')
        return redirect(url_for('auth.change_email_request'))