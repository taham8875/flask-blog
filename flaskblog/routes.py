import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request
from flaskblog import app
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog import bcrypt, db
from flaskblog.models import User
posts = [
    {
        'author': 'taha',
        'title': 'First post',
        'content': 'hello one',
        'data': 'dec 2022'
    },
    {
        'author': 'mom',
        'title': 'second post',
        'content': 'hello two',
        'data': 'nov 2022'
    }
]


@app.route('/')
@app.route('/home')
def home():
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
        return redirect(url_for('home'))

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
            flash('Unsuccessful log in, please check email and password')

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
