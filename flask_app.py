from flask import Flask, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from service import weddingService
import config
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
config.configApp(app)
db = SQLAlchemy(app)

class Household(db.Model):
    __tablename__ = "household"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    uuid = db.Column(db.String(50))
    addresses = db.relationship('Person', backref='household',
                                lazy='dynamic')

class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    email = db.Column(db.String(50))
    invited = db.Column(db.Boolean)
    going = db.Column(db.Boolean)
    invitedRehersal = db.Column(db.Boolean)
    goingRehersal = db.Column(db.Boolean)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))

logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
# set the log handler level
logHandler.setLevel(logging.INFO)
# set the app logger level
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logHandler)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/iceland/")
def iceland():
    return render_template("iceland.html")

@app.route("/wedding/")
def wedding():
    return render_template("wedding.html")

@app.route("/wedding/household/",  methods=["GET", "POST"])
def weddingHousehold():
    if request.method == "GET":
        return weddingService.getHouseholds(app, db)

    return render_template("wedding.html")

@app.route("/test/")
def test():
    return "TEST"
    #app.config["SQLALCHEMY_DATABASE_URI"]

