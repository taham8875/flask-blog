import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message
from flaskblog import myconfig


def set_profile_picture(profile_picture):
    random_hex = secrets.token_hex(8)
    file_name, file_extension = os.path.splitext(profile_picture.filename)
    profile_picture_new_name = random_hex + file_extension
    profile_picture_new_path = os.path.join(
        current_app.root_path, 'static/profile_pics', profile_picture_new_name)
    compressed_profile_picture = Image.open(profile_picture)
    compressed_profile_picture.thumbnail((800, 800))
    compressed_profile_picture.save(profile_picture_new_path)
    return profile_picture_new_name


def send_reset_password_email(user):
    token = user.get_reset_token()
    message = Message('Flask Blog Paswword Reset',
                      sender=myconfig.EMAIL_USER, recipients=[user.email])
    message.body = f'''
To reset your password, visit the following link :
{url_for('users.reset_password', token=token, _external = True)}

if you didn't request a password change token, then simply ignore this email
'''
    mail.send(message)
