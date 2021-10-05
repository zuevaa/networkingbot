from app.User import User

class DbInterface():
    def getUser(self, telegramId):
        pass
    def createUser(self, telegramId, name):
        pass
    def updUser(self, user: User):
        pass
    def clearRunCnt(self):
        pass
    def getEnabledUsers(self):
        pass    
    def getUsersByRunCnt(self, runCnt):
        pass
    def getPairs(self):
        pass
    def insPair(self, telegramId1, telegramId2):
        pass
    def getPairsByDays(self, date):
        pass
    def getPairsByUser(self, telegramId, date):
        pass
    def updatePairStatus(self, telegramId1, telegramId2, status):
        pass
    def insOpinion(self, telegramId1, telegramId2, opinion):
        pass
    def getAdminUsers(self):
        pass
    def getNewUsers(self):
        pass        