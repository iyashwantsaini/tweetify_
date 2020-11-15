from flask import Flask, render_template,flash, redirect,url_for,session,logging,request
import twint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True)
    password = db.Column(db.String(80))
    last_data=db.Column(db.String())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        usr = User.query.filter_by(username=uname, password=passw).first()
        if usr is not None:
            login_user(usr)
            return redirect(url_for("index"))
        else:
            render_template("login.html",message="Invalid Credentials!")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        passw = request.form['passw']
        register = User(username = uname, password = passw)
        db.session.add(register)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html",message="Successfully Logged Out!")

@login_required
@app.route('/index', methods=["POST", "GET"])
def index():
    return render_template('index.html',user_=current_user.username)

data=None

@login_required
@app.route('/results', methods=["POST"])
def result():

    keywords = request.form['keyword']
    noofresults = int(request.form['number'])
    sincedate = request.form['since']
    tilldate = request.form['till']
    location = request.form['location']

    c = twint.Config()
    c.Search = keywords
    c.Limit = noofresults
    c.Since = sincedate
    c.Until = tilldate
    c.Near = location
    c.Pandas = True
    twint.run.Search(c)

    Tweets_df = twint.storage.panda.Tweets_df
    df = Tweets_df[["tweet", "link", "hashtags", "nlikes"]]
    d = df[:noofresults]
    global data
    data = d
    return render_template('results.html', tables=[d.to_html(render_links=True, classes=['table table-hover table-responsive'])], dataframe=d)

@login_required
@app.route('/analysis', methods=["POST", "GET"])
def analysis():
    df = data
    return render_template('analysis.html', tables=[df.to_html(render_links=True, classes=['table table-hover table-responsive'])])


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
