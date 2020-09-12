import os

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json
from datetime import date
from functools import wraps

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("DATABASE_URL")
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=['get','post'])
def index():
    return(render_template("login.html"))

@app.route("/login", methods=['get','post'])
def login():
    session.clear()
    return(render_template("login.html"))

@app.route('/logout')
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/loginstatus", methods=['get', 'post'])
def loginstatus():
    username = request.form.get('username')
    password = request.form.get('password')
    username_list = db.execute("SELECT * from users WHERE username = :username",{'username':username}).fetchone()
    #print(username_list)
    #fetchone() returns tuple
    if(username_list is None):
        return(render_template("error.html", message = "username does not exist"))
    elif(password == username_list[2]):
        session["user_id"] = username_list[0]
        session['user'] = username_list[1]
        return(redirect(url_for('search')))
    return(render_template('error.html',message = "Wrong password"))

@app.route("/register", methods=['get','post'])
def register():
    return(render_template("register.html"))

@app.route("/status", methods=['get','post'])
def status():
    username = request.form.get('username')
    password = request.form.get('password')
    check = request.form.get('check')
    special_chars = '''!@#$%^&*(){[]}|'"?/<>,.+-=\\'''
    sc=False
    for char in password:
        if char in special_chars:
            sc=True
            break
    un = db.execute("SELECT * FROM users WHERE username = :username",{'username':username}).fetchone()
    if(len(username)>5 and un is not None):
        return(render_template('error.html',message='username already exists, please choose another one'))
    elif(len(username)<5):
        return(render_template('error.html', message="Username should contain atleast 5 characters\n"))
    elif(password != check):
        return(render_template("error.html", message="could not match passwords go back and try again"))
    elif(len(password) < 5):
        return(render_template("error.html", message="Password should contain atleast 5 characters\n"))
    elif(sc):
        return(render_template('error.html', message="Password should not contain any special characters\n"))
    else:
        db.execute("INSERT INTO users (username,password) VALUES(:username,:password)",{"username":username,'password':password})
        db.commit()
        return(render_template("success.html"))

@app.route("/search", methods = ['POST','GET'])
@login_required
def search():
    username = session["user"]
    return(render_template('search.html', username=username))

@app.route("/results",methods = ['POST','GET'])
@login_required
def results():
    text = request.form.get("bookname")
    text = text.capitalize()
    if(text is None):
        return(render_template("error.html", messsage = "Proivde author name or ISBN number or Title of book"))
    
    matches = db.execute("SELECT * FROM books WHERE isbn LIKE :text OR title LIKE :text OR author LIKE :text",{'text':'%'+text+'%'}).fetchall()
    print(matches)
    if(len(matches)==0):
        return(render_template("error.html", message="Could not found results"))
    return(render_template("results.html",matches=matches, username=session['user']))

@app.route("/bookpage/<isbn>", methods = ['GET','POST'])
@login_required
def bookpage(isbn):
    apikey = os.getenv("apikey")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": 'apikey', "isbns": isbn})
    response = res.json()
    bookdetails = db.execute("SELECT * FROM books WHERE isbn = :isbn",{'isbn':isbn}).fetchone()
    allreviews = db.execute("SELECT username,comment,rating,time FROM users JOIN reviews ON users.id=reviews.user_id WHERE isbn=:isbn",{'isbn':isbn})
    if(request.method=='POST'):
        #instead of isbn we have to SELECT id FROM books where isbn=isbn and then append that id in book_id field of reviews 
        past_reviews = db.execute("SELECT * FROM reviews WHERE user_id=:user_id AND isbn=:isbn",{'user_id':session["user_id"], 'isbn':isbn}).fetchall()
        print(past_reviews)
        if(len(past_reviews)==0):
            comment = request.form.get("review")
            rating = int(request.form.get("rating"))
            today = str(date.today())
            book_id = db.execute("SELECT id FROM books WHERE isbn=:isbn",{'isbn':isbn}).fetchone()
            db.execute("INSERT INTO reviews (user_id,book_id, isbn, comment, rating, time) VALUES(:userid, :book_id, :isbn,:comment,:rating,:time)",
            {'userid':int(session["user_id"]), 'book_id':book_id[0], 'isbn':isbn, 'comment':comment, 'rating':rating, 'time':today})
            db.commit()
            #allreviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{'isbn':isbn}).fetchall()
            allreviews = db.execute("SELECT username,comment,rating,time FROM users JOIN reviews ON users.id=reviews.user_id WHERE isbn=:isbn",{'isbn':isbn}).fetchall()
            return(render_template("book.html", username=session['user'], submit='True', reviews = allreviews, book=bookdetails, ratings=response['books'][0]))
        return(render_template('book.html',username=session['user'], submit='False', reviews=allreviews,  book=bookdetails, ratings=response['books'][0]))
    else:
        print(allreviews)
        return(render_template("book.html",username=session['user'],submit='None',reviews=allreviews, book=bookdetails, ratings=response['books'][0]))

@app.route("/api/<isbnno>",methods=['GET'])
def api_get(isbnno):
    row = db.execute("SELECT title, author, year, reviews.isbn, COUNT(reviews.id) as review_count,  AVG(reviews.rating) as average_score FROM books INNER JOIN reviews ON books.id = reviews.book_id WHERE reviews.isbn = :isbnno GROUP BY title, author, year, reviews.isbn", {"isbnno": isbnno})
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 404
    tmp = row.fetchone()
    result = dict(tmp.items())
    result['average_score'] = float('%.2f'%(result['average_score']))
    return(jsonify(result))