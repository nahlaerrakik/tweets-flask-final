__author__ = 'nahla.errakik'

import datetime
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

login = LoginManager()
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(50), unique=True)

    @staticmethod
    def get_user(email):
        record = User.query.filter(User.email == email).first()
        if record:
            return User(id=record.id, username=record.username, password=record.password, email=record.email)
        return None

    @staticmethod
    def add_user(username, password, email):
        new_record = User(username=username, password=password, email=email)
        db.session.add(new_record)
        db.session.commit()

    def check_password(self, password):
        return Bcrypt().check_password_hash(self.password, password)

    def __str__(self):
        return '<User %r, %s, %s>' % (self.id, self.username, self.email)


class Search(db.Model, UserMixin):
    __tablename__ = "Search"

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(256))
    text = db.Column(db.String())

    @staticmethod
    def search(keyword):
        result = []
        records = Search.query.filter_by(keyword=keyword).distinct(Search.text).order_by(desc(Search.creation_time))
        for record in records:
            item = Search(id=record.id, creation_time=record.creation_time, keyword=record.keyword, text=record.text)
            result.append(item)
        return result

    @staticmethod
    def add_search(search_item):
        db.session.add(search_item)
        db.session.commit()

    @staticmethod
    def less_than_5minutes(start):
        time_now = datetime.datetime.now()
        time_delta = (time_now - start)
        diff_in_min = time_delta.total_seconds() / 60

        if diff_in_min < 5:
            return True
        else:
            return False


class Tweet(db.Model, UserMixin):
    __tablename__ = "Tweet"

    text = db.Column(db.String(), primary_key=True)
    keyword = db.Column(db.String(256))
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.Column(db.Integer, db.ForeignKey('User.id'))

    @staticmethod
    def add_fav_tweet(keyword, text, user):
        insert_command = Tweet.__table__.insert(
            prefixes=['OR IGNORE'],
            values=dict(text=text, keyword=keyword, user=user)
        )
        db.session.execute(insert_command)
        db.session.commit()

        """db.session.add(new_tweet)
        db.session.commit()"""

    @staticmethod
    def get_fav_tweets(user):
        records = Tweet.query.filter_by(user=user).order_by(desc(Tweet.creation_time))
        return records

    @staticmethod
    def delete_tweet(text):
        db.session.query(Tweet).filter(Tweet.text == text).delete()
        db.session.commit()


@login.user_loader
def load_user(email):
    return User.query.get(email)
