from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem instead of cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensures responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#if session.get("user_id") is None: # Check to ensure a user is logged in
        #return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def index():
    # Accessed via POST (as by submitting a form via POST)
    if request.method == "POST":
        return render_template("index.html")

    # Accessed via GET (as by clicking a link or redirect)
    else:
        return render_template("index.html")

@app.route("/rules", methods=["GET", "POST"])
def rules():
    # Accessed via POST (as by submitting a form via POST)
    if request.method == "POST":
        return render_template("rules.html")

    # Accessed via GET (as by clicking a link or redirect)
    else:
        return render_template("rules.html")

@app.route("/login", methods=["GET", "POST"])
def login(): # Log in a user
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Must Submit Username", code=400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Must Submit Password", code=400)

        # Query database for username
        con = sqlite3.connect("shed.db")
        cur = con.cursor()
        res = cur.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = res.fetchall()
        con.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password")
        ):
            return error("Username Or Passords Do Not Match", code=400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register(): # Register a user
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Must Sumbmit Username", code=400)

        # Ensure username is unique
        con = sqlite3.connect("shed.db")
        cur = con.cursor()
        res = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = res.fetchall()
        con.close()

        if len(rows) >= 1:
            return error("Username Already Exists", code=400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Must Submit Password", code=400)

        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            return error("Must Confirm Password", code=400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return error("Passords Do Not Match", code=400)

        # Start transaction, input data and commit transaction
        con = sqlite3.connect("shed.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (request.form.get("username"),
            generate_password_hash(request.form.get("password")),),
        )
        con.commit()
        con.close()

        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def error(message, code=400): # Render an error message page
    return render_template("apology.html", code=code, message=escape(message))

def escape(string):
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            string = string.replace(old, new)
        return string