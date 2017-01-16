
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/iceland/")
def iceland():
    return render_template("iceland.html")

@app.route("/wedding/")
def wedding():
    return render_template("wedding.html")

