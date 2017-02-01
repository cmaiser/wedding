from flask import Flask, render_template, request, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
import config
import logging
import uuid
import datetime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
config.configApp(app)
db = SQLAlchemy(app)
mail = Mail(app)

class Household(db.Model):
    __tablename__   = "household"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(50))
    uuid            = db.Column(db.String(50))
    sddSent         = db.Column(db.DateTime)
    inviteSent      = db.Column(db.DateTime)
    email           = db.Column(db.String(50))
    emailVerified   = db.Column(db.Boolean)
    addresses       = db.relationship('Person', backref='household', cascade="all, delete-orphan" , lazy='dynamic')
    messages        = db.relationship('Message', backref='household', cascade="all, delete-orphan" , lazy='dynamic')

class Person(db.Model):
    __tablename__   = "person"
    id              = db.Column(db.Integer, primary_key=True)
    firstName       = db.Column(db.String(50))
    lastName        = db.Column(db.String(50))
    going           = db.Column(db.Boolean)
    diet            = db.Column(db.String(500))
    household_id    = db.Column(db.Integer, db.ForeignKey('household.id'))
    #household = db.relationship('Household')

class Message(db.Model):
    __tablename__   = "message"
    id              = db.Column(db.Integer, primary_key=True)
    messageText     = db.Column(db.String(500))
    messageFrom     = db.Column(db.String(50))
    household_id    = db.Column(db.Integer, db.ForeignKey('household.id'))

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

@app.route("/admin/")
def admin():
    return render_template("weddingAdmin.html")

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

@app.route("/wedding/message/", methods=["GET", "POST"])
def weddingMessage():
    if request.method == "GET":
        return jsonify(getMessages())

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


def getMessages():
    returnObject = {}
    results = []

    dbObjects = Message.query.all()
    for n in dbObjects:
        results.append(processMessageForReturn(n))

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

    persons = []
    messages = []

    for n in jsonObj['addresses']:

        if n['id'] is not None:
            personFromDB = Person.query.filter_by(id=n['id']).first()
            db.session.delete(personFromDB)

            try:
                db.session.commit()
            except Exception as e:
                return str(e)

        person = Person(id=None, firstName=n['firstName'], lastName=n['lastName'], going=n['going'], diet=n['diet'])



        persons.append(person)

    for n in jsonObj['messages']:

        if n['id'] is not None:
            messageFromDB = Message.query.filter_by(id=n['id']).first()
            db.session.delete(messageFromDB)

            try:
                db.session.commit()
            except Exception as e:
                return str(e)

        message = Message(id=None, messageText=n['messageText'], messageFrom=n['messageFrom'])
        messages.append(message)

    if jsonObj['id'] is None:

        u = uuid.uuid1()
        uuidStr = u.hex

        household = Household(id= jsonObj['id'], name=jsonObj['name'], uuid=uuidStr, email=jsonObj['email'], emailVerified=jsonObj['emailVerified'], addresses=persons, messages=messages)
        db.session.add(household)

        try:
            db.session.commit()
        except Exception as e:
            return str(e)
    else:

        household = Household.query.filter_by(id=jsonObj['id']).first()
        household.name = jsonObj['name']
        household.email = jsonObj['email']
        if jsonObj['sddSent'] is not None:
            household.sddSent = jsonObj['sddSent']
        if jsonObj['inviteSent'] is not None:
            household.inviteSent = jsonObj['inviteSent']
        if jsonObj['emailVerified'] is not None:
            household.emailVerified = jsonObj['emailVerified']
        household.addresses = persons

        try:
            db.session.commit()
        except Exception as e:
            return str(e)

    #re-query to return results
    dbObject = Household.query.filter_by(id=household.id).first()
    return processHouseholdForReturn(dbObject)

def processMessageForReturn(dbObject):
    message = {}
    message['id']             = dbObject.id
    message['messageText']    = dbObject.messageText
    message['messageFrom']    = dbObject.messageFrom
    message['household_id']   = dbObject.household_id

    return message

#because .__dict__ on complex db objects doesn't seem to work
def processHouseholdForReturn(dbObject):

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
        household['sddSent']            = str(dbObject.sddSent.timestamp())
    if dbObject.inviteSent is not None:
        household['inviteSent']         = str(dbObject.inviteSent.timestamp())

    household['addresses']   = []
    for n in dbObject.addresses.all():
        person = {}
        person['id']              = n.id
        person['firstName']       = n.firstName
        person['lastName']        = n.lastName
        person['going']           = n.going
        person['diet']            = n.diet
        person['household_id']    = n.household_id

        household['addresses'].append(person)

    #Only one message expected...

    messages = []
    for n in dbObject.messages.all():
        message = {}
        message['id']             = n.id
        message['messageText']    = n.messageText
        message['household_id']   = n.household_id

        messages.append(message)
        break

    household['messages'] = messages

    return household

def sendSaveTheDateEmail(household):
    sendEmail("Save the Date!",
               app['ADMINS'][0],
               household.email,
               render_template("saveTheDate.txt",
                               uuid=household.uuid, householdName=household.name),
               render_template("saveTheDate.html",
                               uuid=household.uuid, householdName=household.name))

def sendInviteEmail(household):
    return {}

def sendEmail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)









