import os,requests

from flask import Flask, render_template, redirect, url_for, session, request, g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(40)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template("index.html")

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('search')
    q = "%" + query + "%"
    kk = db.execute("SELECT * FROM books WHERE title LIKE :q OR isbn LIKE :i OR author LIKE :j", {"q": q, "i": q, "j": q}).fetchall()
    return render_template("search_result.html", searchList = kk)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        keyForSignup = 0;
        return render_template("signup.html", keyForSignup = keyForSignup)
    if request.form.get('submitUserSignUp') == "0":
        username = request.form.get('username')
        name = request.form.get('name')
        g.user = username
        g.name = name
        checkUser = db.execute("SELECT * FROM users WHERE username = :u", {"u": username}).first()
        if checkUser is None:
            keyForSignup = 1;
            return render_template("signup.html", keyForSignup = keyForSignup)
        else:
            return render_template("error.html", message = f"Username \"{username}\" is not available. Please create something else.")
    username = str(request.form.get('submitUserSignUp')).split("1", 1)[1]
    name = str(request.form.get('submitUserSignUp')).split("1", 1)[0]
    password = request.form.get('password')
    paswrd = generate_password_hash(str(password))
    db.execute("INSERT INTO users (name, username, password) VALUES(:n, :u, :p)", {"n": name, "u": username, "p": paswrd })
    db.commit()
    return redirect(url_for("login"))


@app.route('/login', methods=[ 'GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    if request.method == 'GET':
        return render_template("login.html")
    username = request.form.get('username')
    password = request.form.get('password')
    checkUsername = db.execute('SELECT * FROM users WHERE username = :u',{"u": username}).first()
    if checkUsername is None:
        return render_template('error.html', message="User Does not Exist.")
    if not check_password_hash(checkUsername.password, str(password)):
        return render_template('error.html', message="Incorrect Password")
    session['user_id'] = checkUsername.id
    name = checkUsername.name
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template('profile.html')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/<book_title>')
def book(book_title):
    if 'user_id' in session:
        kk = str(session['user_id'])
        yourBook = db.execute("SELECT * FROM books WHERE title = :id", {"id": book_title}).fetchone()
        if yourBook is None:
            return render_template('error.html', message = "No Info regarding the book you are looking for.")
        ss = db.execute("SELECT * FROM ratereview WHERE user_id = :U AND book_id = :B",{"U": kk, "B": yourBook.id}).fetchone()
        if ss is None:
            return render_template('book.html', buk = yourBook, rate="Rate it How you experienced.", review="Review The Book.")
        if ss.rating is None:
            return render_template('book.html', buk = yourBook, rate="Rate it How you experienced.", review= ss.review)
        if ss.review is None:
            return render_template('book.html', buk = yourBook, rate=ss.rating, review="Review The Book.")
        return render_template('book.html', buk = yourBook, rate=ss.rating, review=ss.review)
    return redirect(url_for('index'))

@app.route('/review/<book_id>',methods=['GET','POST'])
def review(book_id):
    if 'user_id' in session:
        kk = str(session['user_id'])
        if int(book_id)>300:
            return render_template('error.html', message= 'The book does not exist in our database.')
        buk = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        checkUB = db.execute("SELECT * FROM ratereview WHERE user_id = :U AND book_id = :B",{"U": kk, "B": buk.id}).fetchone()
        if request.method == "GET":
            if checkUB is None:
                return render_template('book.html', buk = buk, reviewKey="1111", rate="Rate it How you experienced.", review="Review The Book.")
            if checkUB.rating is None:
                return render_template('book.html', buk = buk, reviewKey="1111", rate="Rate it How you experienced.", review= checkUB.review)
            if checkUB.review is None:
                return render_template('book.html', buk = buk, reviewKey="1111", rate=checkUB.rating, review="Review The Book.")
            return render_template('book.html', buk = buk, reviewKey="1111", rate=checkUB.rating, review=checkUB.review)
        review = request.form.get('reviewarea')
        if checkUB is None:
            db.execute("INSERT INTO ratereview (user_id, book_id, review) VALUES (:U, :B, :RE)",{"U": kk, "B": buk.id, "RE": review})
            db.commit()
            return render_template('book.html', buk = buk,rate="Rate it How you experienced.", review=review)
        if checkUB.review is None:
            db.execute("UPDATE ratereview SET review = :RE WHERE user_id = :U AND book_id = :B",{"RE": review, "U": kk, "B": buk.id})
            db.commit()
            return render_template('book.html', buk = buk,rate = checkUB.rating, review=review)
        db.execute("UPDATE ratereview SET review = :RE WHERE user_id = :U AND book_id = :B",{"RE": review, "U": kk, "B": buk.id})
        db.commit()
        if checkUB.rating is None:
            return render_template('book.html', buk = buk,rate="Rate it How you experienced.", review=review)
        return render_template('book.html', buk = buk,rate = checkUB.rating, review=review)
    return redirect(url_for('index'))

@app.route('/rate/<book_id>',methods=['GET','POST'])
def rate(book_id):
    if 'user_id' in session:
        kk = str(session['user_id'])
        if int(book_id)>300:
            return render_template('error.html', message= 'The book does not exist in our database.')
        buk = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        checkUB = db.execute("SELECT * FROM ratereview WHERE user_id = :U AND book_id = :B",{"U": kk, "B": buk.id}).fetchone()
        if request.method == "GET":
            if checkUB is None:
                return render_template('book.html', buk = buk, rateKey="0000", rate="Rate it How you experienced.", review="Review The Book.")
            if checkUB.rating is None:
                return render_template('book.html', buk = buk, rateKey="0000", rate="Rate it How you experienced.", review= checkUB.review)
            if checkUB.review is None:
                return render_template('book.html', buk = buk, rateKey="0000", rate=checkUB.rating, review="Review The Book.")
            return render_template('book.html', buk = buk, rateKey="0000", rate=checkUB.rating, review=checkUB.review)
        rate = request.form.get('rating')
        if checkUB is None:
            db.execute("INSERT INTO ratereview (user_id, book_id, rating) VALUES (:U, :B, :R)",{"U": kk, "B": buk.id, "R": rate})
            db.commit()
            return render_template('book.html', buk = buk, rate = rate, review="Review The Book.")
        if checkUB.rating is None:
            db.execute("UPDATE ratereview SET rating = :R WHERE user_id = :U AND book_id = :B",{"R": rate,"U": kk, "B": buk.id})
            db.commit()
            return render_template('book.html', buk = buk, rate = rate, review=checkUB.review)
        db.execute("UPDATE ratereview SET rating = :R WHERE user_id = :U AND book_id = :B",{"R": rate,"U": kk, "B": buk.id})
        db.commit()
        if checkUB.review is None:
            return render_template('book.html', buk = buk, rate = rate,review="Review The Book.")
        return render_template('book.html', buk = buk, rate = rate, review=checkUB.review)
    return redirect(url_for('index'))

@app.route('/goodreads_reviews/isbn/<book_isbn>', methods=['GET','POST'])
def goodreads(book_isbn):
    if 'user_id' in session:
        kk = str(session['user_id'])
        buk = db.execute("SELECT * FROM books WHERE isbn = :id", {"id": book_isbn}).fetchone()
        if buk is None:
            return render_template('error.html', message= f"Book with ISBN \"{book_isbn}\" is not in our Database. Please check the URL or Search again.")
        ss = db.execute("SELECT * FROM ratereview WHERE user_id = :U AND book_id = :B",{"U": kk, "B": buk.id}).fetchone()
        if request.method == "GET":
            if ss is None:
                return render_template('book.html', buk = buk, rate="Rate it How you experienced.", review="Review The Book.")
            if ss.rating is None:
                return render_template('book.html', buk = buk, rate="Rate it How you experienced.", review= ss.review)
            if ss.review is None:
                return render_template('book.html', buk = buk, rate=ss.rating, review="Review The Book.")
            return render_template('book.html', buk = buk, rate=ss.rating, review=ss.review)
        try:
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BpmVmMTdAtNjJJZhdnbSQ", "isbns": f"{buk.isbn}"})
        except:
            return render_template('error.html', message="Network error. Check your connection.")
        avgR = res.json()["books"][0]['average_rating']
        rateC = res.json()["books"][0]['ratings_count']
        revC = res.json()["books"][0]['reviews_count']
        isbn13 = res.json()["books"][0]['isbn13']
        if ss is None:
            return render_template('book.html', buk = buk, goodreadsKey = "2222", rate="Rate it How you experienced.", review="Review The Book.",avgR =avgR, rateC = rateC, revC = revC, isbn13 = isbn13)
        if ss.rating is None:
            return render_template('book.html', buk = buk, goodreadsKey = "2222", rate="Rate it How you experienced.", review= ss.review,avgR =avgR, rateC = rateC, revC = revC, isbn13 = isbn13)
        if ss.review is None:
            return render_template('book.html', buk = buk, goodreadsKey = "2222", rate=ss.rating, review="Review The Book.",avgR =avgR, rateC = rateC, revC = revC, isbn13 = isbn13)
        return render_template('book.html', buk = buk, goodreadsKey = "2222", rate=ss.rating, review=ss.review,avgR =avgR, rateC = rateC, revC = revC, isbn13 = isbn13)
    return redirect(url_for('index'))
