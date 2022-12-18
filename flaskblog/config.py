import os
import flaskblog.myconfig as myconfig


class Config:
    SECRET_KEY = myconfig.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = myconfig.SQLALCHEMY_DATABASE_URI
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = myconfig.EMAIL_USER
    MAIL_PASSWORD = myconfig.EMAIL_PASSWORD
