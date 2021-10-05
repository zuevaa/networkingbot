class User():
    def __init__(self, telegramId, name, pic, job, interest, city, skill, type, enabled, runCnt, isNew, isAdmin, wizardStage):
        self.telegramId = telegramId
        self.name = name
        self.pic = pic
        self.job = job
        self.interest = interest
        self.city = city
        self.skill = skill
        self.type = type
        self.enabled = enabled
        self.runCnt = runCnt
        self.pairs = []
        self.currentPairs = []
        self.todayPair = 0
        self.isNew = isNew
        self.isAdmin = isAdmin
        self.wizardStage = wizardStage

    def isFull(self):
        if (self.name == '' or self.name == None or
            self.pic == '' or self.pic == None or
            self.job == '' or self.job == None or
            self.interest == '' or self.interest == None or
            self.city == '' or self.city == None or
            self.skill == ''or self.skill == None):
            return 0
        else:
            return 1
