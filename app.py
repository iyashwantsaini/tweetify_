from flask import Flask, render_template, request, url_for
import twint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def login():
    return render_template('login.html')

@app.route('/index', methods=["POST", "GET"])
def index():
    username = request.form['username']
    password = request.form['password']
    if(username=='thapar' and password=='thapar'):
        return render_template('index.html')
    

data = None


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


@app.route('/analysis', methods=["POST", "GET"])
def analysis():
    df = data
    return render_template('analysis.html', tables=[df.to_html(render_links=True, classes=['table table-hover table-responsive'])])


if __name__ == '__main__':
    app.run(debug=True)
