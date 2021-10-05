from db.DbHelper import DbHelper
import schedule
import time
import threading
import config
from random import shuffle
from datetime import datetime, timedelta

class Scheduler():
    def __init__(self, bot, dbHelper):
        self._bot = bot
        self._dbHelper = dbHelper
        #run users ask
        schedule.every().monday.at(config.MESSAGE_TIME).do(self.askRunCnt)
        schedule.every().monday.at(config.MESSAGE_TIME).do(self.newUserReminder)
        #calculate pair at tuesday, thursday, saturday
        schedule.every().tuesday.at('00:00').do(self.calculatePair, 1)
        schedule.every().thursday.at('00:00').do(self.calculatePair, 2)
        schedule.every().saturday.at('00:00').do(self.calculatePair, 3)
        #send pair at message time
        schedule.every().tuesday.at(config.MESSAGE_TIME).do(self.sendPair)
        schedule.every().thursday.at(config.MESSAGE_TIME).do(self.sendPair)
        schedule.every().saturday.at(config.MESSAGE_TIME).do(self.sendPair)
        #send reminder
        schedule.every().wednesday.at(config.MESSAGE_TIME).do(self.sendReminder)
        schedule.every().friday.at(config.MESSAGE_TIME).do(self.sendReminder)
        schedule.every().sunday.at(config.MESSAGE_TIME).do(self.sendReminder)
        #check meet
        schedule.every().sunday.at(config.MESSAGE_TIME).do(self.checkMeet)
        threading.Thread(target=self.scheduleThread).start()
    
    def scheduleThread(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def askRunCnt(self):
        self._dbHelper.clearRunCnt()
        userList = self._dbHelper.getEnabledUsers()        
        for user in userList:
            self._bot.askRunCnt(user)

    def newUserReminder(self):
        userList = self._dbHelper.getNewUsers()
        for user in userList:
            self._bot.newUserReminder(user)        

    def calculatePair(self, runCnt):
        userList = self._dbHelper.getUsersForPair(runCnt)
        shuffle(userList)
        for user in userList:
            if (   (user.todayPair > 0 and user.type == 1)
                or (user.todayPair > 1 and user.type == 2)):
                continue
            for user2 in userList:
                if (user.telegramId == user2.telegramId):
                    continue
                if (   (user2.todayPair > 0 and user2.type == 1)
                    or (user2.todayPair > 1 and user2.type == 2)):
                    continue
                if ( user.telegramId in user2.pairs):
                    continue
# here we can add adddition check for ex by city

                self._dbHelper.insPair(user.telegramId, user2.telegramId)
                user.todayPair += 1
                user.pairs.append(user2.telegramId)
                user2.todayPair += 1
                user2.pairs.append(user.telegramId)

                if (   (user.todayPair > 0 and user.type == 1)
                    or (user.todayPair > 1 and user.type == 2)):
                    break

    def sendPair(self):
        rows = self._dbHelper.getPairsByDays(datetime.today().strftime('%Y%m%d'))
        userMap = {}
        userList = []
        for row in rows:
            if (row[0] not in userMap):    
                userMap[str(row[0])] = self._dbHelper.getUser(row[0])
                userList.append(userMap[str(row[0])])
            if (row[1] not in userMap):    
                userMap[str(row[1])] = self._dbHelper.getUser(row[1])
                userList.append(userMap[str(row[1])])

            userMap[str(row[0])].currentPairs.append(userMap[str(row[1])])
            userMap[str(row[1])].currentPairs.append(userMap[str(row[0])])
        
        for user in userList:
            self._bot.sendPair(user)

    def sendReminder(self):
        rows = self._dbHelper.getPairsByDays((datetime.today()- timedelta(days=1)).strftime('%Y%m%d'))
        for row in rows:
            self._bot.sendReminder(row[0])
            self._bot.sendReminder(row[1])

    def checkMeet(self):
        userList = self._dbHelper.getUsersForPair(1)
        for user in userList:
            pairUserList = self._dbHelper.getPairsByUser(user.telegramId, (datetime.today()- timedelta(weeks=1)).strftime('%Y%m%d'))
            self._bot.checkMeet(user.telegramId, pairUserList, 0)