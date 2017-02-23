from flask import render_template
from flask_mail import Message
import uuid
import datetime

def getActivity(Activity):
    returnObject = {}
    results = []

    dbObjects = Activity.query.all()
    for n in dbObjects:
        results.append(processActivityForReturn(n))

    returnObject['results'] = results
    return returnObject

def getComments(Comments):
    returnObject = {}
    results = []

    dbObjects = Comments.query.all()
    for n in dbObjects:
        results.append(processCommentForReturn(n))

    returnObject['results'] = results
    return returnObject

def getHouseholds(Household, db, Activity):

    returnObject = {}
    results = []

    dbObjects = Household.query.all()
    for n in dbObjects:
        results.append(processHouseholdForReturn(db, Activity, n))

    returnObject['results'] = results
    return returnObject

def getHousehold(Household, uuid, db, Activity):
    household = Household.query.filter_by(uuid=uuid).first()
    return processHouseholdForReturn(db, Activity, household)

def saveActivity(db, Activity, severity, householdName, text):

    activityDate = datetime.datetime.now()

    activity = Activity(activityDate=activityDate, severity=severity, householdName=householdName, text=text)
    db.session.add(activity)

    try:
        db.session.commit()
    except Exception as e:
        return str(e)

def saveHousehold(db, Person, Comments, Household, Activity, jsonObj):

    saveActivity(db, Activity, "INFO", jsonObj['name'], "Saving household")

    persons = []
    comments = []

    for n in jsonObj['persons']:

        if n['id'] is not None:
            personFromDB = Person.query.filter_by(id=n['id']).first()
            db.session.delete(personFromDB)

            try:
                db.session.commit()
            except Exception as e:
                saveActivity(db, Activity, "ERROR", jsonObj['name'], str(e))

        person = Person(id=None, firstName=n['firstName'], lastName=n['lastName'], going=n['going'], diet=n['diet'])
        persons.append(person)

    for n in jsonObj['comments']:

        if n['id'] is not None:
            commentFromDB = Comments.query.filter_by(id=n['id']).first()
            db.session.delete(commentFromDB)

            try:
                db.session.commit()
            except Exception as e:
                saveActivity(db, Activity, "ERROR", jsonObj['name'], str(e))

        comment = Comments(id=None, commentText=n['commentText'], commentFrom=n['commentFrom'])
        comments.append(comment)

    saveActivity(db, Activity, "DEBUG", jsonObj['name'], "Adding " + str(len(persons)) + " persons")
    saveActivity(db, Activity, "DEBUG", jsonObj['name'], "Adding " + str(len(comments)) + " comments")

    if jsonObj['id'] is None:

        saveActivity(db, Activity, "DEBUG", jsonObj['name'], "Inserting new household")

        u = uuid.uuid1()
        uuidStr = u.hex

        household = Household(id= jsonObj['id'], name=jsonObj['name'], uuid=uuidStr, email=jsonObj['email'], emailVerified=jsonObj['emailVerified'], persons=persons, comments=comments)
        db.session.add(household)

        try:
            db.session.commit()
        except Exception as e:
            saveActivity(db, Activity, "ERROR", jsonObj['name'], str(e))
    else:

        saveActivity(db, Activity, "DEBUG", jsonObj['name'], "Updating existing household")

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
            saveActivity(db, Activity, "ERROR", jsonObj['name'], str(e))

    saveActivity(db, Activity, "DEBUG", jsonObj['name'], "Querying for return household.")
    #re-query to return results
    dbObject = Household.query.filter_by(id=household.id).first()

    return processHouseholdForReturn(db, Activity, dbObject)


#because .__dict__ on complex db objects doesn't seem to work
def processActivityForReturn(dbObject):
    activity = {}
    activity['activityDate'] = dbObject.activityDate
    activity['severity'] = dbObject.severity
    activity['householdName'] = dbObject.householdName
    activity['text'] = dbObject.text

    return activity;

#because .__dict__ on complex db objects doesn't seem to work
def processCommentForReturn(dbObject):
    comment = {}
    comment['id']             = dbObject.id
    comment['commentText']    = dbObject.commentText
    comment['commentFrom']    = dbObject.commentFrom
    comment['household_id']   = dbObject.household_id

    return comment

#because .__dict__ on complex db objects doesn't seem to work
def processHouseholdForReturn(db, Activity, dbObject):

    saveActivity(db, Activity, "DEBUG", dbObject.name, "Processing household for return.")

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

def sendSaveTheDateEmail(db, Activity, household, mail):

    saveActivity(db, Activity, "INFO", household['name'], "Sending Save the Date to " + household['email'])

    return sendEmail("Save the Date!",
               "invites@chrisandcandice.com",
               [household['email']],
               render_template("saveTheDate.txt",
                               uuid=household['uuid'], householdName=household['name']),
               render_template("saveTheDate.html",
                               uuid=household['uuid'], email=household['email'], name=household['name']),
                mail, db, Activity)

def sendInviteEmail(db, Activity, household, mail):

    saveActivity(db, Activity, "INFO", household['name'], "Sending Invite to " + household['email'])

    return sendEmail("Maiser + Walkinshaw Wedding Invitation",
               "invites@chrisandcandice.com",
               [household['email']],
               render_template("invitation.txt",
                               uuid=household['uuid'], householdName=household['name']),
               render_template("invitation.html",
                               uuid=household['uuid'], email=household['email'], name=household['name']),
                mail, db, Activity)

def sendConfirmationEmail(db, Activity, household, mail):

    saveActivity(db, Activity, "INFO", household['name'], "Sending Confirmation to " + household['email'])

    return sendEmail("Maiser + Walkinshaw Wedding RSVP Confirmation",
               "invites@chrisandcandice.com",
               [household['email']],
               render_template("confirmation.txt",
                               uuid=household['uuid'], householdName=household['name']),
               render_template("confirmation.html",
                               uuid=household['uuid'], email=household['email'], name=household['name'], persons=household['persons']),
                mail, db, Activity)

def sendEmail(subject, sender, recipients, text_body, html_body, mail, db, Activity):

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

    msg.body = text_body
    msg.html = html_body

    try:
        mail.send(msg)
    except Exception as e:
        saveActivity(db, Activity, "ERROR", recipients[0], str(e))

    return "success"