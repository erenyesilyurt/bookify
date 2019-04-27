from flask_sqlalchemy import SQLAlchemy
from application import db


class User(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)


class Book(db.Model):
    __tablename__ = 'books'
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    reviews = db.relationship('Review', lazy=True)

    def add_review(self, userid, rating, text):
        r = Review(userid=userid, isbn=self.isbn, rating=rating, text=text)
        db.session.add(r)
        db.session.commit()

    def user_has_reviewed(self, userid):
        r = Review.query.filter_by(userid=userid, isbn=self.isbn).first()
        if r is None:
            return False
        else:
            return True


class Review(db.Model):
    __tablename__ = 'reviews'
    reviewid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'),
                       nullable=False)
    isbn = db.Column(db.String, db.ForeignKey('books.isbn'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)
