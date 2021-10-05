import config
from app.User import User
from db.DbInterface import DbInterface
from db.DbPostgreSql import DbPostgreSql


class DbHelper():
    def __init__(self):
        if config.DB == 'postgresql':
            self._db = DbPostgreSql()
        else:
            raise RuntimeError

    def getUser(self, telegramId):
        row = self._db.getUser(telegramId)
        if (row == None):
            return None
        user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
        return user        
    def createUser(self, telegramId, name):
        user = self.getUser(telegramId)
        if (user == None):        
            self._db.createUser(telegramId, name)   
            user = self.getUser(telegramId)
            user.isNew = True
        return user
    def updUser(self, user: User):
        return self._db.updUser(user)   
    def clearRunCnt(self):
        self._db.clearRunCnt()
    def getEnabledUsers(self):
        rows = self._db.getEnabledUsers()
        userList = []
        for row in rows:
            user = self.getUser(row[0])
            userList.append(user)
        return userList
    def getUsersForPair(self, runCnt):
        rows = self._db.getUsersByRunCnt(runCnt)
        userList = []
        userMap = {}
        for row in rows:
            user = self.getUser(row[0])
            userList.append(user)  
            userMap[user.telegramId] = user
        rows = self._db.getPairs()
        for row in rows:
            user = userMap[row[0]]
            user.pairs.append(row[1])
            user = userMap[row[1]]
            user.pairs.append(row[0])
        return userList
    def insPair(self, telegramId1, telegramId2):
        self._db.insPair(telegramId1, telegramId2)
    def getPairsByDays(self, date):
        return self._db.getPairsByDays(date)
    def getPairsByUser(self, telegramId, date):
        rows = self._db.getPairsByUser(telegramId, date)
        userList = []
        for row in rows:
            if (row[0] == telegramId):
                user = self.getUser(row[1])
            else:
                user = self.getUser(row[0])
            userList.append(user)
        return userList
    def updatePairStatus(self, telegramId1, telegramId2, status, date):
        self._db.updatePairStatus(telegramId1, telegramId2, status, date)
    def insOpinion(self, telegramId1, telegramId2, opinion):
        self._db.insOpinion(telegramId1, telegramId2, opinion)
    def getAdminUsers(self):
        rows = self._db.getAdminUsers()
        userList = []
        for row in rows:
            user = self.getUser(row[0])
            userList.append(user)
        return userList
    def getNewUser(self):
        rows = self._db.getNewUser()
        userList = []
        for row in rows:
            user = self.getUser(row[0])
            userList.append(user)
        return userList