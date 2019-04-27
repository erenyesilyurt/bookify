from application import app, db
import config
from models import User, Book
from flask import (Flask, render_template, session,
                   redirect, url_for, request, abort)
from passlib.hash import pbkdf2_sha256
import requests


@app.route('/')
def index():
    if 'username' in session:
        # user is logged in, render their homepage
        return render_template('home.html', username=session['username'])
    else:
        # not logged in, redirect to sign in page
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        pw = request.form.get('password').strip()

        if username == '' or pw == '':
            return abort(400)

        user = User.query.filter_by(
            username=username).first()
        if user is None:
            return render_template('login.html', err_user_not_found=True)

        if (pbkdf2_sha256.verify(pw, user.password_hash)):
            session['userid'] = user.userid
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', err_password_incorrect=True)

    else:
        # show the login form alongside with a registration link
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # validate form info and register the user
        username = request.form.get('username').strip()
        pw = request.form.get('password').strip()
        email = request.form.get('email').strip()

        if username == '' or pw == '':
            return abort(400)

        if User.query.filter_by(
                username=request.form.get('username')).first() is not None:
            return render_template('register.html', err_username_exists=True)

        if email != '':
            if User.query.filter_by(
                    email=request.form.get('email')).first() is not None:
                return render_template('register.html', err_email_exists=True)

        pw_hash = pbkdf2_sha256.hash(pw)
        user = User(username=username, password_hash=pw_hash, email=email)
        db.session.add(user)
        db.session.commit()
        return render_template('register_success.html', username=username)

    else:
        # show the registration form
        return render_template('register.html')


@app.route('/search')
def search():
    query = request.args.get('q', default='', type=str).strip()
    findBy = request.args.get('findBy', default='title', type=str)

    if query == '':
        return abort(400)

    if findBy == 'title':
        books = Book.query.filter(Book.title.startswith(query)).all()
    elif findBy == 'isbn':
        books = Book.query.filter(Book.isbn.startswith(query)).all()
    elif findBy == 'author':
        books = Book.query.filter(Book.author.startswith(query)).all()
    else:
        return abort(400)

    return render_template('search_results.html', books=books, query=query)


@app.route('/book/<isbn>')
def book(isbn):
    book = Book.query.get_or_404(isbn)
    goodreads_data = requests.get(config.GOODREADS_URL,
                                  params={'key': config.GOODREADS_KEY, 'isbns': isbn})
    goodreads_data = goodreads_data.json()

    return render_template('book.html', book=book,
                           goodreads_data=goodreads_data)


@app.route('/book/<isbn>/submit_review', methods=['POST'])
def submit_review(isbn):
    if 'username' not in session:
        return render_template('login.html')

    userid = session['userid']
    book = Book.query.get_or_404(isbn)

    if book.user_has_reviewed(session['userid']):
        msg = 'You have already written a review for this book.'
        result = 'Sorry, but we couldn\'t add your review!'
        return render_template('result.html', success=False,
                               result_message=msg, result=result,
                               result_backlink=url_for('book', isbn=isbn))

    rating = request.form.get('rating').strip()
    text = request.form.get('text').strip()
    if rating == '' or text == '':
        return abort(400)

    rating = int(rating)
    if rating < 0 or rating > 5:
        return abort(400)

    book.add_review(userid, rating, text)

    result = 'Success!'
    msg = 'Your review has been successfuly submitted.'
    return render_template('result.html', success=True,
                           result_message=msg, result=result,
                           result_backlink=url_for('book', isbn=isbn))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))