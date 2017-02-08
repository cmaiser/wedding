from flask import Flask, render_template, request, jsonify, Response, flash, redirect, session, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import config
import logging
import uuid
import datetime
import os
from logging.handlers import RotatingFileHandler

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
    comments = getComments()
    return render_template("wedding.html", comments=comments['results'])

@app.route("/admin/")
def admin():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("weddingAdmin.html")

@app.route('/login', methods=['POST'])
def adminLogin():
    if request.form['password'] == app.config['ADMIN_PASSWORD'] and request.form['username'] == app.config['ADMIN_USER_NAME']:
        session['logged_in'] = True
        return render_template("weddingAdmin.html")
    else:
        return render_template('login.html')

@app.route("/wedding/household/",  methods=["GET", "POST"])
def weddingHousehold():
    if request.method == "GET":
        return jsonify(getHouseholds())
    else:
        jsonObj = request.get_json(force=True)

        #sddSent, inviteSent, emailVerified not updated on save
        jsonObj['sddSent'] = None
        jsonObj['inviteSent'] = None
        jsonObj['emailVerified'] = None

        return jsonify(saveHousehold(jsonObj))

@app.route("/wedding/household/<uuid>")
def weddingSingleHousehold(uuid):
    return jsonify(getHousehold(uuid))

@app.route("/wedding/activity/", methods=["GET", "POST"])
def weddingActivity():
    if request.method == "GET":
        return jsonify(getActivity())

@app.route("/wedding/comment/", methods=["GET", "POST"])
def weddingComment():
    if request.method == "GET":
        return jsonify(getComments())

@app.route("/wedding/sendSaveTheDate/<uuid>")
def sendSaveTheDate(uuid):
    household = getHousehold(uuid)
    if household:
        sendSaveTheDateEmail(household)

        household['sddSent'] = datetime.datetime.now()
        household['inviteSent'] = None
        household['emailVerified'] = None

        return jsonify(saveHousehold(household))

@app.route("/wedding/sendInvite/<uuid>")
def sendInvite(uuid):
    household = getHousehold(uuid)
    if household:
        sendInviteEmail(household)

        household['inviteSent'] = datetime.datetime.now()
        household['sddSent'] = None
        household['emailVerified'] = None

        return jsonify(saveHousehold(household))

@app.route("/wedding/verifyEmail/<uuid>")
def verifyEmail(uuid):
    household = getHousehold(uuid)
    if household:
        household['emailVerified'] = True
        household['inviteSent'] = None
        household['sddSent'] = None

        saveHousehold(household)
        return render_template("weddingEmail.html", uuid=household['uuid'])

def getActivity():
    returnObject = {}
    results = []

    dbObjects = Activity.query.all()
    for n in dbObjects:
        results.append(processActivityForReturn(n))

    returnObject['results'] = results
    return returnObject

def getComments():
    returnObject = {}
    results = []

    dbObjects = Comments.query.all()
    for n in dbObjects:
        results.append(processCommentForReturn(n))

    returnObject['results'] = results
    return returnObject

def getHouseholds():

    returnObject = {}
    results = []

    dbObjects = Household.query.all()
    for n in dbObjects:
        results.append(processHouseholdForReturn(n))

    returnObject['results'] = results
    return returnObject

def getHousehold(uuid):
    household = Household.query.filter_by(uuid=uuid).first()
    return processHouseholdForReturn(household)

def saveHousehold(jsonObj):

    saveActivity("INFO", jsonObj['name'], "Saving household")

    persons = []
    comments = []

    for n in jsonObj['persons']:

        if n['id'] is not None:
            personFromDB = Person.query.filter_by(id=n['id']).first()
            db.session.delete(personFromDB)

            try:
                db.session.commit()
            except Exception as e:
                saveActivity("ERROR", jsonObj['name'], str(e))

        person = Person(id=None, firstName=n['firstName'], lastName=n['lastName'], going=n['going'], diet=n['diet'])
        persons.append(person)

    for n in jsonObj['comments']:

        if n['id'] is not None:
            commentFromDB = Comments.query.filter_by(id=n['id']).first()
            db.session.delete(commentFromDB)

            try:
                db.session.commit()
            except Exception as e:
                saveActivity("ERROR", jsonObj['name'], str(e))

        comment = Comments(id=None, commentText=n['commentText'], commentFrom=n['commentFrom'])
        comments.append(comment)

    saveActivity("DEBUG", jsonObj['name'], "Adding " + str(len(persons)) + " persons")
    saveActivity("DEBUG", jsonObj['name'], "Adding " + str(len(comments)) + " comments")

    if jsonObj['id'] is None:

        saveActivity("DEBUG", jsonObj['name'], "Inserting new household")

        u = uuid.uuid1()
        uuidStr = u.hex

        household = Household(id= jsonObj['id'], name=jsonObj['name'], uuid=uuidStr, email=jsonObj['email'], emailVerified=jsonObj['emailVerified'], persons=persons, comments=comments)
        db.session.add(household)

        try:
            db.session.commit()
        except Exception as e:
            saveActivity("ERROR", jsonObj['name'], str(e))
    else:

        saveActivity("DEBUG", jsonObj['name'], "Updating existing household")

        household = Household.query.filter_by(id=jsonObj['id']).first()
        household.name = jsonObj['name']
        household.email = jsonObj['email']
        if jsonObj['sddSent'] is not None:
            household.sddSent = jsonObj['sddSent']
        if jsonObj['inviteSent'] is not None:
            household.inviteSent = jsonObj['inviteSent']
        if jsonObj['emailVerified'] is not None:
            household.emailVerified = jsonObj['emailVerified']
        household.persons = persons
        household.comments = comments

        try:
            db.session.commit()
        except Exception as e:
            saveActivity("ERROR", jsonObj['name'], str(e))

    saveActivity("DEBUG", jsonObj['name'], "Querying for return household.")
    #re-query to return results
    dbObject = Household.query.filter_by(id=household.id).first()
    return processHouseholdForReturn(dbObject)

def processActivityForReturn(dbObject):
    activity = {}
    activity['activityDate'] = dbObject.activityDate
    activity['severity'] = dbObject.severity
    activity['householdName'] = dbObject.householdName
    activity['text'] = dbObject.text

    return activity;

def processCommentForReturn(dbObject):
    comment = {}
    comment['id']             = dbObject.id
    comment['commentText']    = dbObject.commentText
    comment['commentFrom']    = dbObject.commentFrom
    comment['household_id']   = dbObject.household_id

    return comment

#because .__dict__ on complex db objects doesn't seem to work
def processHouseholdForReturn(dbObject):

    saveActivity("DEBUG", dbObject.name, "Processing household for return.")

    household = {}

    if dbObject is None:
        return household

    household['id']          = dbObject.id
    household['name']        = dbObject.name
    household['uuid']        = dbObject.uuid
    household['email']       = dbObject.email
    if dbObject.emailVerified is not None:
        household['emailVerified']      = dbObject.emailVerified
    if dbObject.sddSent is not None:
        household['sddSent']            = str(dbObject.sddSent)
    if dbObject.inviteSent is not None:
        household['inviteSent']         = str(dbObject.inviteSent)

    household['persons']   = []
    for n in dbObject.persons.all():
        person = {}
        person['id']              = n.id
        person['firstName']       = n.firstName
        person['lastName']        = n.lastName
        person['going']           = n.going
        person['diet']            = n.diet
        person['household_id']    = n.household_id

        household['persons'].append(person)

    #Only one comment expected...

    comments = []
    for n in dbObject.comments.all():
        comment = {}
        comment['id']             = n.id
        comment['commentText']    = n.commentText
        comment['commentFrom']    = n.commentFrom
        comment['household_id']   = n.household_id

        comments.append(comment)
        break

    household['comments'] = comments

    return household

def saveActivity(severity, householdName, text):

    activityDate = datetime.datetime.now()

    activity = Activity(activityDate=activityDate, severity=severity, householdName=householdName, text=text)
    db.session.add(activity)

    try:
        db.session.commit()
    except Exception as e:
        return str(e)

def sendSaveTheDateEmail(household):

    saveActivity("INFO", household['name'], "Sending Save the Date to " + household['email'])

    return sendEmail("Save the Date!",
               "chrisandcandicetest@gmail.com",
               [household['email']],
               render_template("saveTheDate.txt",
                               uuid=household['uuid'], householdName=household['name']),
               render_template("saveTheDate.html",
                               uuid=household['uuid'], email=household['email'], name=household['name']))

def sendInviteEmail(household):

    saveActivity("INFO", household['name'], "Sending Invite to " + household['email'])

    return sendEmail("Maiser + Walkinshaw Wedding Invitation",
               "chrisandcandicetest@gmail.com",
               [household['email']],
               render_template("invitation.txt",
                               uuid=household['uuid'], householdName=household['name']),
               render_template("invitation.html",
                               uuid=household['uuid'], email=household['email'], name=household['name']))

def sendEmail(subject, sender, recipients, text_body, html_body):

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

    msg.body = text_body
    msg.html = html_body

    with app.open_resource("./static/wedding/assets/img/ico/linebreak.PNG") as fp:
        msg.attach("linebreak.png", "image/png", fp.read())

    try:
        mail.send(msg)
    except Exception as e:
        saveActivity("ERROR", recipients[0], str(e))

    return "success"