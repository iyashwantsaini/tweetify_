from flask import Flask, render_template,flash, redirect,url_for,session,logging,request
from flask.helpers import make_response
from pandas.core.series import Series
import twint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import paralleldots
import io
import base64

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def paralleldots_api(text):
    api_key = "DgACcdya0nNxCxWOeKHDmEsEMIWtMDRds9PPwx5nmGc"
    paralleldots.set_api_key(api_key)
    text_todo=text
    emot=paralleldots.emotion(text_todo)
    # print(emot) #emotion analysis
    # intent=paralleldots.intent(text_todo)
    # print(intent) #Intent analyisis
    # return {'emotion':emot,'intent':intent}
    return emot

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

@login_required
@app.route('/results', methods=["POST", "GET"])
def result():

    c = twint.Config()
    keywords = request.form['keyword']
    noofresults = int(request.form['number'])
    sincedate = request.form['since']
    tilldate = request.form['till']
    location = request.form['location']

    c.Search = keywords
    c.Limit = noofresults
    c.Since = sincedate
    c.Until = tilldate
    c.Near = location
    c.Pandas = True
    twint.run.Search(c)
    tweets_df = twint.storage.panda.Tweets_df

    # df = Tweets_df[["tweet", "link", "hashtags", "nlikes"]]
    df = tweets_df[["tweet", "link"]]
    df_final = df[0:noofresults]
    df_final.columns=["Tweet","Link"]

    # saving to session of current user
    session["data_current"] = df_final.to_json()
    return render_template('results.html', tables=[df_final.to_html(render_links=True, classes=['table align-middle'])])

@login_required
@app.route('/dwn_csv', methods=["POST", "GET"])
def dwn_csv():
    df_from_session = session.get('data_current')
    df = pd.read_json(df_from_session, dtype=False)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=tweets.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@login_required
@app.route('/dwn_json', methods=["POST", "GET"])
def dwn_json():
    df_from_session = session.get('data_current')
    resp = make_response(df_from_session)
    resp.headers["Content-Disposition"] = "attachment; filename=tweets.json"
    resp.headers["Content-Type"] = "application/json"
    return resp

@login_required
@app.route('/analysis', methods=["POST", "GET"])
def analysis():
    df_from_session = session.get('data_current')
    df = pd.read_json(df_from_session, dtype=False)
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    
    happy=0
    angry=0
    bored=0
    fear=0
    sad=0
    excited=0

    for i in df.index: 
        curr_ans=paralleldots_api(df['Tweet'][i])['emotion']
        happy+=curr_ans['Happy']
        angry+=curr_ans['Angry']
        bored+=curr_ans['Bored']
        fear+=curr_ans['Fear']
        sad+=curr_ans['Sad']
        excited+=curr_ans['Excited']

    print(happy,angry,bored,fear,sad,excited)

    data=[happy,angry,bored,fear,sad,excited]
    emotions=["Happy","Angry","Bored","Fear","Sad","Excited"]

    fig = plt.figure(figsize =(10, 7)) 
    plt.pie(data, labels = emotions) 
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return render_template('analysis.html', tables=[df.to_html(render_links=True, classes=['table align-middle'])], plot_url=plot_url)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
