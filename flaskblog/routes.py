from flask import render_template
from flaskblog import app

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
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')
