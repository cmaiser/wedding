def configApp(app):

    username = ""
    password = ""
    hostname = "nnagflar.mysql.pythonanywhere-services.com"
    databasename = "nnagflar$wedding"

    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{fusername}:{fpassword}@{fhostname}/{fdatabasename}".format(
        fusername=username,
        fpassword=password,
        fhostname=hostname,
        fdatabasename=databasename
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config['SQLALCHEMY_ECHO'] = True
    app.config["DEBUG"] = True


    app.config["MAIL_SERVER"] = 'smtp.googlemail.com'
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = ""
    app.config["MAIL_PASSWORD"] = password

    # administrator list
    app.config["ADMINS"] = [""]