from flask import Flask, render_template, request, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from logging.handlers import RotatingFileHandler

from service.weddingService import sendSaveTheDateEmail
from service.weddingService import sendInviteEmail
from service.weddingService import sendConfirmationEmail
from service.weddingService import getHousehold
from service.weddingService import getHouseholds
from service.weddingService import getComments
from service.weddingService import getActivity
from service.weddingService import saveHousehold

import config
import datetime
import logging
import os

app = Flask(__name__)
config.configApp(app)
db = SQLAlchemy(app)
mail = Mail(app)

app.secret_key = os.urandom(12)

class Household(db.Model):
    __tablename__   = "household"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(50))
    uuid            = db.Column(db.String(50))
    sddSent         = db.Column(db.DateTime)
    inviteSent      = db.Column(db.DateTime)
    email           = db.Column(db.String(50))
    emailVerified   = db.Column(db.Boolean)
    persons         = db.relationship('Person',   backref='household', cascade="all, delete-orphan" , lazy='dynamic')
    comments        = db.relationship('Comments', backref='household', cascade="all, delete-orphan" , lazy='dynamic')

class Person(db.Model):
    __tablename__   = "person"
    id              = db.Column(db.Integer, primary_key=True)
    firstName       = db.Column(db.String(50))
    lastName        = db.Column(db.String(50))
    going           = db.Column(db.Boolean)
    diet            = db.Column(db.String(500))
    household_id    = db.Column(db.Integer, db.ForeignKey('household.id'))
    #household = db.relationship('Household')

class Comments(db.Model):
    __tablename__   = "comments"
    id              = db.Column(db.Integer, primary_key=True)
    commentText     = db.Column(db.String(500))
    commentFrom     = db.Column(db.String(50))
    household_id    = db.Column(db.Integer, db.ForeignKey('household.id'))

class Activity(db.Model):
    __tablename__   = "activity"
    id              = db.Column(db.Integer, primary_key=True)
    activityDate    = db.Column(db.DateTime)
    severity        = db.Column(db.String(50))
    householdName   = db.Column(db.String(50))
    text            = db.Column(db.String(500))

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
    comments = getComments(Comments)
    return render_template("wedding.html", comments=comments['results'])

@app.route("/wedding/admin/")
def admin():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("weddingAdmin.html")

@app.route('/wedding/admin/login', methods=['POST'])
def adminLogin():
    if request.form['password'] == app.config['ADMIN_PASSWORD'] and request.form['username'] == app.config['ADMIN_USER_NAME']:
        session['logged_in'] = True
        return render_template("weddingAdmin.html")
    else:
        return render_template('login.html')

@app.route("/wedding/household/",  methods=["GET", "POST"])
def weddingHousehold():
    if request.method == "GET":
        return jsonify(getHouseholds(Household, db, Activity))
    else:
        jsonObj = request.get_json(force=True)

        #sddSent, inviteSent, emailVerified not updated on save
        jsonObj['sddSent'] = None
        jsonObj['inviteSent'] = None
        jsonObj['emailVerified'] = None

        response = saveHousehold(db, Person, Comments, Household, Activity, jsonObj)

        if(len(response['persons']) > 0):
            if(response['persons'][0]['going'] is not None):
                sendConfirmationEmail(db, Activity, response, mail)

        return jsonify(response)

@app.route("/wedding/household/<uuid>")
def weddingSingleHousehold(uuid):
    return jsonify(getHousehold(Household, uuid, db, Activity))

@app.route("/wedding/activity/", methods=["GET", "POST"])
def weddingActivity():
    if request.method == "GET":
        return jsonify(getActivity(Activity))

@app.route("/wedding/comment/", methods=["GET", "POST"])
def weddingComment():
    if request.method == "GET":
        return jsonify(getComments())

@app.route("/wedding/sendSaveTheDate/<uuid>")
def sendSaveTheDate(uuid):
    household = getHousehold(Household, uuid, db, Activity)
    if household:
        sendSaveTheDateEmail(db, Activity, household, mail)

        household['sddSent'] = datetime.datetime.now()
        household['inviteSent'] = None
        household['emailVerified'] = None

        return jsonify(saveHousehold(db, Person, Comments, Household, Activity, household))

@app.route("/wedding/sendInvite/<uuid>")
def sendInvite(uuid):
    household = getHousehold(Household, uuid, db, Activity)
    if household:
        sendInviteEmail(db, Activity, household, mail)

        household['inviteSent'] = datetime.datetime.now()
        household['sddSent'] = None
        household['emailVerified'] = None

        return jsonify(saveHousehold(db, Person, Comments, Household, Activity, household))

@app.route("/wedding/verifyEmail/<uuid>")
def verifyEmail(uuid):
    household = getHousehold(Household, uuid, db, Activity)
    if household:
        household['emailVerified'] = True
        household['inviteSent'] = None
        household['sddSent'] = None

        saveHousehold(db, Person, Comments, Household, Activity, household)
        return render_template("weddingEmail.html", uuid=household['uuid'])

