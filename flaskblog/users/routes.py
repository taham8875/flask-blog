import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, redirect, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import send_reset_password_email, set_profile_picture
from flaskblog import bcrypt, db, mail
from flaskblog.models import User, Post

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already registered, if you want to create a new account, log out from the current one', 'info')
        return redirect(url_for('main.home'))

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
        return redirect(url_for('users.login'))

    return render_template('register.jinja2', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in, if you want to log in with another account, log out from the current one', 'info')
        return redirect(url_for('main.home'))

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
                return redirect(url_for('main.home'))
        else:
            flash('Unsuccessful log in, please check email and password', 'danger')

    return render_template('login.jinja2', title='Log in', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out', 'info')
    return redirect(url_for('users.login'))


@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.jinja2', title='Account', form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(
        Post.date.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.jinja2', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_password_email(user)
        flash(
            f'Please check the email address {form.email.data} for instructions to reset your password.\nIf you can\'t find the email, check the spams folder', 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset.jinja2', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('users.request_reset'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(
            f'New password has ben updated {user.username}, You can log in now', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.jinja2', title='Reset Password', form=form)
