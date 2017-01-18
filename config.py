def configApp(app):

    username = "nnagflar"
    password = "romica666"
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

    app.config["DEBUG"] = True