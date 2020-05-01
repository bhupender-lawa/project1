import os

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
        yourBook = db.execute("SELECT * FROM books WHERE title = :id", {"id": book_title}).fetchone()
        if yourBook is None:
            return render_template('error.html', message = "No Info regarding the book you are looking for.")
        return render_template('book.html', buk = yourBook)
    return redirect(url_for('index'))

@app.route('/review/<book_id>',methods=['GET','POST'])
def review(book_id):
    if 'user_id' in session:
        buk = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        if request.method == "GET":
            return render_template('book.html', buk = buk, reviewKey="1111")
        return render_template('book.html', buk = buk)
    return redirect(url_for('index'))

@app.route('/rate/<book_id>',methods=['GET','POST'])
def rate(book_id):
    if 'user_id' in session:
        if int(book_id)>300:
            return render_template('error.html', message= 'The book does not exist in our database.')
        buk = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        if request.method == "GET":
            return render_template('book.html', buk = buk, rateKey="0000")
        return render_template('book.html', buk = buk)
    return redirect(url_for('index'))
