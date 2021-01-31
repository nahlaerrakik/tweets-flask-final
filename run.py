__author__ = 'nahla.errakik'

import json
from flask import Flask, render_template, request, redirect, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from models import User, Search, Tweet, login, db
from pyTwitter import Twitter

app = Flask(__name__)
if app.config['ENV'] == 'production':
    app.config.from_object('config.ProdConfig')

elif app.config['ENV'] == 'testing':
    app.config.from_object('config.TestConfig')

else:
    app.config.from_object('config.DevConfig')

bcrypt = Bcrypt(app)
db.init_app(app)
login.init_app(app)


@app.before_first_request
def create_all():
    db.create_all()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    try:
        if current_user.is_authenticated:
            print("ICH BIN IN LOGIN")
            return redirect('/')

        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User().get_user(email)

            if user is None:
                flash('User {} not found.'.format(email), 'warning')
                return render_template('login.html')

            elif not user.check_password(password):
                flash('Password is not correct.', 'warning')
                return render_template('login.html')
            else:
                login_user(user)
                return redirect('/')
        else:
            return render_template('login.html')
    except:
        flash(app.config['ERROR_MSG'].format('Could not login'), 'warning')
        return redirect('/login')


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route("/register", methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            repeat_password = request.form['repeat_password']

            user = User().get_user(email)

            if user:
                flash('User already exist !', 'danger')
                return render_template('register.html')

            elif password != repeat_password:
                flash('Passwords do not match !', 'danger')
                return render_template('register.html')

            else:
                hash_password = bcrypt.generate_password_hash(password)
                User().add_user(username, hash_password, email)

                flash('Congrats! you have successfully registered. You can login now !', 'success')
                return render_template('login.html')

        return render_template('register.html')
    except:
        flash(app.config['ERROR_MSG'].format('Could not load page'), 'danger')
        return render_template('register.html')


@app.route("/search", methods=['GET'])
def search():
    try:
        myTwitter = Twitter({'key': app.config['TWITTER_API_CLIENT_KEY'], 'secret': app.config['TWITTER_API_CLIENT_SECRET']})
        keyword = request.args.get('keyword')
        tweets = Search().search(keyword)

        if len(tweets) > 0:
            if Search.less_than_5minutes(tweets[0].creation_time):
                tweets = [{'text': x.text} for x in tweets]
            else:
                print("insert new tweets in db")
                search_result = myTwitter.search_tweets(keyword)
                tweets = search_result['statuses']
                for item in tweets:
                    tweet = Search(keyword=keyword, text=item['text'])
                    Search().add_search(tweet)
        # Keyword isn t in DB
        else:
            print("!!!!!!!!!!!NOT FOUND IN DATABASE")
            search_result = myTwitter.search_tweets(keyword)
            tweets = search_result['statuses']
            for item in tweets:
                tweet = Search(keyword=keyword, text=item['text'])
                Search().add_search(tweet)

        if len(tweets) <= 0:
            flash('No results were found.', 'warning')
        else:
            flash('{} results were found.'.format(len(tweets)), 'success')

        return render_template("index.html", tweets=tweets, keyword=keyword, tweetsy=json.dumps(tweets))
    except:
        flash(app.config['ERROR_MSG'].format('Could not get search results'), 'danger')
        return render_template("index.html", keyword=request.args.get('keyword'))


@app.route("/store", methods=['GET', 'POST'])
@login_required
def store():
    try:
        keyword = request.form['keyword']
        tweets = json.loads(request.form['tweetsy'])
        for tweet in tweets:
            text = tweet['text']
            Tweet.add_fav_tweet(keyword, text, current_user.id)

        flash('Your search for the Keyword # {} # was successfully stored.'.format(keyword), 'success')
        return render_template("index.html", tweets=tweets, keyword=keyword, tweetsy=json.dumps(tweets))
    except:
        flash(app.config['ERROR_MSG'].format('Could not store tweets!'), 'danger')
        return redirect("/search")


@app.route("/profile")
@login_required
def profile():
    user_fav_tweets = Tweet.get_fav_tweets(user=current_user.id)
    return render_template('profile.html', stored_tweets=user_fav_tweets)


@app.route("/delete_tweet", methods=['POST'])
@login_required
def delete_tweet():
    try:
        tweet_id = request.form['tweet_id']
        Tweet.delete_tweet(tweet_id)
        flash('Your Tweet was successfully deleted', 'success')
        return redirect('/profile')
    except:
        flash(app.config['ERROR_MSG'].format('Could not delete tweet!'), 'danger')
        return redirect('/profile')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found_404.html')


if __name__ == "__main__":
    app.run()
