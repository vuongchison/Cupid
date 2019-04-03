from flask import render_template, redirect, url_for, flash, abort, request, current_app
from . import main
from app.models import User, Post
from flask_login import login_required, current_user
from .forms import InformationForm, PostForm, EditPostForm, ChangeAvatarForm
from app import db
from werkzeug.utils import secure_filename
import os

@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            p = Post(body=form.body.data, author_id = current_user.id)
            db.session.add(p)
            db.session.commit()
            flash('Đăng thành công.')
            return redirect(url_for('main.index'))

        page = request.args.get('page', 1, type=int)
        pagination =  Post.query.filter(Post.author != current_user).order_by(Post.created.desc()).paginate(page, per_page=20, error_out=False)
        posts = pagination.items
        return render_template('index.html', form=form, posts=posts, pagination=pagination)
    
    else:
        return render_template('intro.html')

@main.route('/test')
def test():
    return render_template('test_success.html')

@main.route('/user')
@login_required
def user_homepage():
    return redirect(url_for('main.user', uuid=current_user.uuid))

@main.route('/user/<uuid>')
@login_required
def user(uuid):
    u = User.query.filter_by(uuid=uuid).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination =  u.posts.order_by(Post.created.desc()).paginate(page, per_page=20, error_out=False)
    posts = pagination.items
    return render_template('user.html', user=u, posts=posts, pagination=pagination)

@main.route('/edit-info', methods=['GET', 'POST'])
@login_required
def edit_info():
    form = InformationForm(current_user)
    if form.validate_on_submit():
        current_user.birthday = form.birthday.data
        current_user.gender_id = form.gender.data if form.gender.data != 0 else None
        current_user.province_id = form.province.data if form.province.data != 0 else None
        current_user.phone_number = form.phone_number.data
        current_user.about_me = form.about_me.data
        current_user.height = form.height.data if form.height.data != 0 else None
        current_user.weight = form.weight.data if form.weight.data != 0 else None
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('main.user', uuid=current_user.uuid))
    else:
        form.birthday.data = current_user.birthday
        form.gender.data = current_user.gender_id or 0
        form.province.data = current_user.province_id or 0
        form.height.data = current_user.height or 0
        form.weight.data = current_user.weight or 0
        form.phone_number.data = current_user.phone_number
        form.about_me.data = current_user.about_me
        return render_template('edit_info.html', form=form)

@main.route('/setting')
@login_required
def setting():
    return render_template('setting.html')


@main.route('/post/<uuid>')
@login_required
def post(uuid):
    p = Post.query.filter_by(uuid=uuid).first_or_404()
    return render_template('post.html', post=p)

@main.route('/edit-post/<uuid>', methods=['GET', 'POST'])
@login_required
def edit_post(uuid):
    p = Post.query.filter_by(uuid=uuid).first_or_404()
    if p.author_id != current_user.id:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        p.body = form.body.data
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('main.post', uuid=uuid))
    form.body.data = p.body
    return render_template('edit_post.html', form=form)

@main.route('/delete-post/<uuid>')
@login_required
def delete_post(uuid):
    p = Post.query.filter_by(uuid=uuid).first_or_404()
    if p.author_id != current_user.id:
        abort(403)
    db.session.delete(p)
    db.session.commit()
    next = request.args.get('next')
    if next is None:
        return redirect(url_for('main.index'))
    else:
        return redirect(next)

@main.route('/people')
@login_required
def people():
    page = request.args.get('page', 1, type=int)
    pagination =  User.query.filter(User.gender_id != current_user.gender_id).paginate(page, per_page=20, error_out=False)
    people = pagination.items
    return render_template('people.html', people=people, pagination=pagination)
    
@main.route('/change-avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        if form.submit.data:
            f = form.newavatar.data
            filename = secure_filename(str(current_user.uuid) + '.png')
            f.save(os.path.join(current_app.config.get('BASEDIR'), 'app/static/img/avatar', filename))
            current_user.avatar = filename
            db.session.add(current_user)
            db.session.commit()

        return redirect(url_for('main.user_homepage'))
    
    return render_template('change_avatar.html', form=form)