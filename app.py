from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
import facebook as fb
import urllib2
import json
from pprint import pprint
from flask_bootstrap import Bootstrap
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '201049237061460',
        'secret': 'b0628ba953c46beba8b8dc9473d7d4c0'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listings')
def listings():
    print "listings"
    print access
    url = "https://graph.facebook.com/v2.8/me/accounts?access_token={0}".format(access)
    print url
    a = urllib2.urlopen("https://graph.facebook.com/v2.8/me/accounts?access_token=EAAC22mxbf1QBADounJZBd9bUZAkb65PJMW6dbFZA9lZAIuA26jeDEtq7uX33heJ17rQZBGFaMHGvalClZBw2BT2GxWVvInUK9hJOy8ZA9FKjWDL5vZCNgtZBM9uAnNTiN8hv8sE1aYf9BYC92HTSq8TXtzwHjms6c3ZCMZD").read()
    a = json.loads(a)
    print a
    return render_template('listings.html', a=a)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    pprint (vars(oauth))
    social_id, username, email, access_token = oauth.callback()
    global access
    access =  access_token
    print access

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
