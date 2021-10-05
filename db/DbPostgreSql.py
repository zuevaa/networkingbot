import config
import psycopg2
from app.User import User
from db.DbInterface import DbInterface

class DbPostgreSql(DbInterface):
    def __init__(self):
        self.connection = psycopg2.connect(host = config.DB_HOST,
                                           user = config.DB_USER,
                                           password = config.DB_PASSWORD,
                                           dbname = config.DB_DATABASE)
    def getUser(self, telegramId):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id, name, pic, job, interest, city, skill, type, enabled, run_cnt, is_new, is_admin, wizard_stage from users where telegram_id = %s', (telegramId,))
        row = cursor.fetchone()
        return row
    def createUser(self, telegramId, name):
        cursor = self.connection.cursor()
        cursor.execute('insert into users (telegram_id, name, type, enabled, is_new, is_admin, wizard_stage) values (%s, %s, 1, 0, 1, 0, %s)', (telegramId, name, 'name'))
        self.connection.commit()
    def updUser(self, user: User):
        cursor = self.connection.cursor()
        cursor.execute('update users set name = %s, pic = %s, job = %s, interest = %s, city = %s, skill = %s, type = %s, enabled = %s, run_cnt = %s, is_new = %s, wizard_stage = %s where telegram_id = %s', 
                       (user.name, user.pic, user.job, user.interest, user.city, user.skill, user.type, user.enabled, user.runCnt, user.isNew, user.wizardStage, user.telegramId, ))
        self.connection.commit()
        return user
    def clearRunCnt(self):
        cursor = self.connection.cursor()
        cursor.execute('update users set run_cnt = null')
        self.connection.commit()        
    def getEnabledUsers(self):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id from users where enabled = 1')
        rows = cursor.fetchall()
        return rows     
    def getUsersByRunCnt(self, runCnt):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id from users where enabled = 1 and run_cnt >= %s', (runCnt,))
        rows = cursor.fetchall()
        return rows
    def getPairs(self):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id1, telegram_id2, date, status from pair where status = 1 or status is null')
        rows = cursor.fetchall()
        return rows        
    def insPair(self, telegramId1, telegramId2):
        cursor = self.connection.cursor() 
        cursor.execute('insert into pair (telegram_id1, telegram_id2, date) values (%s, %s, CURRENT_DATE)', (telegramId1, telegramId2,))
        self.connection.commit()        
    def getPairsByDays(self, date):
        cursor = self.connection.cursor()
        cursor.execute("select telegram_id1, telegram_id2, date, status from pair where date = TO_DATE(%s, 'YYYYMMDD')", (date,))
        rows = cursor.fetchall()
        return rows          
    def getPairsByUser(self, telegramId, date):
        cursor = self.connection.cursor()
        cursor.execute("select telegram_id1, telegram_id2, date, status from pair where (telegram_id1 = %s or telegram_id2 = %s) and date > TO_DATE(%s, 'YYYYMMDD') order by date, telegram_id1, telegram_id2", (telegramId, telegramId, date,))
        rows = cursor.fetchall()
        return rows          
    def updatePairStatus(self, telegramId1, telegramId2, status, date):
        cursor = self.connection.cursor()
        cursor.execute("update pair set status = case when status is null or status = 0 then %s else status end where telegram_id1 = %s and telegram_id2 = %s and date > TO_DATE(%s, 'YYYYMMDD')", (status, telegramId1, telegramId2, date,))
        cursor.execute("update pair set status = case when status is null or status = 0 then %s else status end where telegram_id2 = %s and telegram_id1 = %s and date > TO_DATE(%s, 'YYYYMMDD')", (status, telegramId1, telegramId2, date,))
        self.connection.commit()          
    def insOpinion(self, telegramId1, telegramId2, opinion):
        cursor = self.connection.cursor()
        cursor.execute('insert into opinion (telegram_id1, telegram_id2, opinion, date) values (%s, %s, %s, CURRENT_DATE)', (telegramId1, telegramId2, opinion,))
        self.connection.commit()  
    def getAdminUsers(self):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id from users where is_admin = 1')
        rows = cursor.fetchall()
        return rows     
    def getNewUsers(self):
        cursor = self.connection.cursor()
        cursor.execute('select telegram_id from users where is_new = 1')
        rows = cursor.fetchall()
        return rows  