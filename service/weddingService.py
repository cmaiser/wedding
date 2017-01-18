from dao import weddingDao

def getHouseholds(app, db):
    return weddingDao.getHouseholds(app, db)

def saveHouseholds(app, db):
    return weddingDao.saveHousehold(app, db)