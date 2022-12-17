import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flaskblog import app, bcrypt, db, mail
from flaskblog.models import User, Post
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.date.desc()).paginate(page=page, per_page=5)
    return render_template('home.jinja2', posts=posts)


@app.route('/about')
def about():
    return render_template('about.jinja2')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already registered, if you want to create a new account, log out from the current one', 'info')
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(
            f'New account is created for {form.username.data}, You can log in now', 'success')
        return redirect(url_for('login'))

    return render_template('register.jinja2', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flash('You are already logged in, if you want to log in with another account, log out from the current one', 'info')
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Successful login', 'success')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Unsuccessful log in, please check email and password', 'danger')

    return render_template('login.jinja2', title='Log in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out')
    return redirect(url_for('login'))


def set_profile_picture(profile_picture):
    random_hex = secrets.token_hex(8)
    file_name, file_extension = os.path.splitext(profile_picture.filename)
    profile_picture_new_name = random_hex + file_extension
    profile_picture_new_path = os.path.join(
        app.root_path, 'static/profile_pics', profile_picture_new_name)
    compressed_profile_picture = Image.open(profile_picture)
    compressed_profile_picture.thumbnail((800, 800))
    compressed_profile_picture.save(profile_picture_new_path)
    return profile_picture_new_name


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            current_user.profile_picture = set_profile_picture(
                form.profile_picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account info updated successfully', 'success')
        return redirect(url_for('account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.jinja2', title='Account', form=form)


@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('New post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.jinja2', title='New Post', form=form)


@app.route('/posts/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.jinja2', title=post.title, post=post)


@app.route('/posts/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update_post.jinja2', title='Update Post', form=form)


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(
        Post.date.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.jinja2', posts=posts, user=user)


def send_reset_password_email(user):
    token = user.get_reset_token()
    email_sender = os.environ.get('EMAIL_USER')
    message = Message('Flask Blog Paswword Reset',
                      sender='flaskblogtaha@gmail.com', recipients=[user.email])
    # print('taha')
    # print(message)
    # print(message.sender)
    message.body = f'''
To reset your password, visit the following link :
{url_for('reset_password', token=token, _external = True)}

if you didn't request a password change token, then simply ignore this email
'''
    mail.send(message)


@app.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_password_email(user)
        flash(
            f'Please check the email address {form.email.data} for instructions to reset your password.\nIf you can\'t find the email, check the spams folder', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.jinja2', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(
            f'New password has ben updated {user.username}, You can log in now', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.jinja2', title='Reset Password', form=form)
