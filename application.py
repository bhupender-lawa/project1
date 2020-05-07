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

################################################################################################################################################################

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template("index.html")


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
    # name = checkUsername.name
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template('profile.html')
    return redirect(url_for('index'))


@app.route('/search', methods=['POST'])
def search():
    if 'user_id' in session:
        query = request.form.get('search')
        q = "%" + query + "%"
        kk = db.execute("SELECT * FROM books WHERE title LIKE :q OR isbn LIKE :i OR author LIKE :j", {"q": q, "i": q, "j": q}).fetchall()
        return render_template("search_result.html", searchList = kk)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

################################################################################################################################################################

@app.route('/<int:book_id>')
def book(book_id):
    if 'user_id' in session:
        kk= str(session['user_id'])
        book = db.execute("SELECT * FROM books WHERE id = :t",{"t": book_id}).fetchone()
        rare = db.execute("SELECT * FROM ratereview WHERE user_id =  :u AND book_id = :b",{"u": kk, "b": book.id}).fetchone()
        try:
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BpmVmMTdAtNjJJZhdnbSQ", "isbns": f"{book.isbn}"})
        except:
            return render_template("error.html", message=f"Check your \'connection\' or the url input")
        avgR = res.json()['books'][0]['average_rating']
        ratC = res.json()['books'][0]['ratings_count']
        count = db.execute("SELECT * FROM countnavg WHERE book_id = :b",{"b": book_id}).fetchone()
        if count is not None:
            avgRb = count.avg
            ratCb = count.count
        else:
            avgRb = "Please rate and review."
            ratCb = "Be the First one to rate and review."
        if rare is None:
            return render_template('book.html', book= book, rarekey=0, avgR=avgR, ratC=ratC, avgRb=avgRb, ratCb= ratCb)
        rating = rare.rating
        review = rare.review
        return render_template('book.html', book= book, rating=rating, review=review, avgR=avgR, ratC=ratC, avgRb=avgRb, ratCb= ratCb)
    return redirect(url_for('index'))

@app.route('/rate/<book_id>', methods=['POST'])
def rare(book_id):
    if 'user_id' in session:
        kk= str(session['user_id'])
        rating = request.form.get('rate')
        review = request.form.get("reviewarea")
        avgncount = db.execute("SELECT * FROM countnavg WHERE book_id = :b",{"b": book_id}).fetchone()
        if avgncount is None:
            db.execute("INSERT INTO countnavg (book_id, avg, count) VALUES (:b, :a, 1)",{"b": book_id, "a": int(rating)})
            db.commit()
        else:
            count = avgncount.count
            avg = avgncount.avg
            avg = ((avg * count + int(rating)) / (count+1))
            db.execute("UPDATE countnavg SET avg = :a, count = :c WHERE book_id = :b",{"a": avg, "c": count+1, "b": book_id})
            db.commit()
        db.execute("INSERT INTO ratereview (user_id, book_id, rating, review) VALUES (:u, :b, :r, :re)",{"u": kk, "b": book_id, "r": rating, "re": review})
        db.commit()
        return redirect(url_for('book', book_id=book_id))
    return redirect(url_for('index'))

################################################################################################################################################################

@app.route('/api/<isbn>')
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :i",{"i": isbn}).fetchone()
    if book is None:
        return render_template('error.html', message=f"404 Error! Requested book assosciated with ISBN \"{isbn}\" not found.")
    avgncount = db.execute("SELECT * FROM countnavg WHERE book_id = :b",{"b": book.id}).fetchone()
    json = {"title": f"{book.title}",
            "author": f"{book.author}",
            "year": f"{book.year}",
            "isbn": f"{book.isbn}",
            "review_count": f"{avgncount.count}",
            "average_score": f"{avgncount.avg}"}
    return json
