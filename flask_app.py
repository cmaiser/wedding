from flask import Flask, render_template, request, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
import config
import logging
import uuid
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
config.configApp(app)
db = SQLAlchemy(app)

class Household(db.Model):
    __tablename__   = "household"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(50))
    uuid            = db.Column(db.String(50))
    addresses       = db.relationship('Person', backref='household', cascade="all, delete-orphan" , lazy='dynamic')

class Person(db.Model):
    __tablename__   = "person"
    id              = db.Column(db.Integer, primary_key=True)
    firstName       = db.Column(db.String(50))
    lastName        = db.Column(db.String(50))
    email           = db.Column(db.String(50))
    invited         = db.Column(db.Boolean)
    going           = db.Column(db.Boolean)
    invitedRehersal = db.Column(db.Boolean)
    goingRehersal   = db.Column(db.Boolean)
    household_id    = db.Column(db.Integer, db.ForeignKey('household.id'))
    #household = db.relationship('Household')

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
        return jsonify(saveHouseholds(jsonObj))

@app.route("/test/")
def test():
    return "TEST"

def getHouseholds():

    returnObject = {}
    results = []

    dbObjects = Household.query.all()
    for n in dbObjects:
        results.append(processHouseholdForReturn(n))

    returnObject['results'] = results
    return returnObject

def saveHouseholds(jsonObj):

    persons = []

    for n in jsonObj['addresses']:

        if n['id'] is not None:
            personFromDB = Person.query.filter_by(id=n['id']).first()
            db.session.delete(personFromDB)

            try:
                db.session.commit()
            except Exception as e:
                return str(e)

        person = Person(id=None, firstName=n['firstName'], lastName=n['lastName'], email=n['email'], invited=n['invited'], going=n['going'], invitedRehersal=n['invitedRehersal'], goingRehersal=n['goingRehersal'])
        persons.append(person)



    if jsonObj['id'] is None:

        u = uuid.uuid1()
        uuidStr = u.hex

        household = Household(id= jsonObj['id'], name=jsonObj['name'], uuid=uuidStr, addresses=persons)
        db.session.add(household)

        try:
            db.session.commit()
        except Exception as e:
            return str(e)
    else:
        household = Household.query.filter_by(id=jsonObj['id']).first()
        household.name = jsonObj['name']
        household.addresses = persons

        try:
            db.session.commit()
        except Exception as e:
            return str(e)

    #re-query to return results
    dbObject = Household.query.filter_by(id=household.id).first()

    return processHouseholdForReturn(dbObject)

#because .__dict__ on complex db objects doesn't seem to work
def processHouseholdForReturn(dbObject):

    household = {};
    household['id']          = dbObject.id
    household['name']        = dbObject.name
    household['uuid']        = dbObject.uuid
    household['addresses']   = []

    for n in dbObject.addresses.all():
        person = {}
        person['id']              = n.id
        person['firstName']       = n.firstName
        person['lastName']        = n.lastName
        person['email']           = n.email
        person['invited']         = n.invited
        person['going']           = n.going
        person['invitedRehersal'] = n.invitedRehersal
        person['goingRehersal']   = n.goingRehersal
        person['household_id']    = n.household_id

        household['addresses'].append(person)

    return household











