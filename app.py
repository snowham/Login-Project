from flask import Flask, render_template, redirect, url_for, request, flash
import dbFuncs, twitter, sqlite3, json, requests, os
import tweepy as tw
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('login_project_secret_key') #Replace this with some random string to prevent hackers from getting information you don't want them to see!

'''
Twitter API authentication. If you want to clone this code,
make sure you make your own twitter developer account and get
your authentication keys
'''
consumer_key = os.environ.get('twitter_consumer_key')
consumer_secret = os.environ.get('twitter_consumer_secret')
token_key = os.environ.get('twitter_token_key')
token_secret = os.environ.get('twitter_token_secret')

session = dict() # user_ip:username


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_ip = request.environ['REMOTE_ADDR'] if request.environ.get('HTTP_X_FORWARDED_FOR') is None else request.environ['HTTP_X_FORWARDED_FOR']
    if user_ip in session:
        flash(f"Already logged in to {session[user_ip]}!")
        return redirect(url_for('home'))
    error = ''
    if request.method == 'POST':
        username, password = request.form['username'].strip(), request.form['password'].strip()
        session[user_ip] = username
        if dbFuncs.isNewUsername(username) and username!='' and password!='':
            dbFuncs.addNewUser(username, password)
            return redirect(url_for('home'))
        elif username=='' or password=='':
            error = 'Please enter a none-empty username and password.'
        else:
            completion = dbFuncs.validate(username, password)
            if not completion:
                error = 'Invalid Credentials. Please try again.'
            else:
                return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/user', methods=['GET', 'POST'])
def user():
    user_ip = request.environ['REMOTE_ADDR'] if request.environ.get('HTTP_X_FORWARDED_FOR') is None else request.environ['HTTP_X_FORWARDED_FOR']
    if user_ip not in session:
        flash("Please login before entering the user page.")
        return redirect(url_for('login'))
    changeUsernameError = False
    tweets = []
    if request.method == 'POST' and 'newUsername' in request.form:
        oldUsername = session[user_ip]
        newUsername, password = request.form['newUsername'].strip(), request.form['password'].strip()
        if dbFuncs.validate(oldUsername, password) and newUsername!='' and dbFuncs.isNewUsername(newUsername):
            dbFuncs.changeUsername(oldUsername, newUsername)
            session[user_ip] = newUsername
        else:
            changeUsernameError = True
    elif request.method == 'POST' and 'hashtag' in request.form:
        hashtag = request.form['hashtag'].strip()
        if any(punc in hashtag for punc in ' `~!@#$%^&*()_-+={}[]|\:;<,>.?/\'\"') or hashtag == '':
            return render_template('user.html', twitterError=True, tweets=[], changeUsernameError=False, username=session[user_ip])
        tweets = twitter.getTweets(hashtag, consumer_key, consumer_secret, token_key, token_secret)
    return render_template('user.html', twitterError=False, tweets=tweets, changeUsernameError=changeUsernameError, username=session[user_ip])


@app.route('/logout')
def logout():
    user_ip = request.environ['REMOTE_ADDR'] if request.environ.get('HTTP_X_FORWARDED_FOR') is None else request.environ['HTTP_X_FORWARDED_FOR']
    if user_ip in session:
        session.pop(user_ip, 0)
        flash("Logged out!")
    else:
        flash("You aren't logged in, so how would you be able to logout?")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80")
