import config
import telebot
from telebot import types
from datetime import datetime, timedelta
import threading

class Bot():
    def __init__(self, dbHelper):
        self._dbHelper = dbHelper
        self.bot = telebot.TeleBot(config.TELEGRAM_KEY)
        @self.bot.message_handler(commands = 'start')
        def start(message):
            user = self._dbHelper.createUser(message.chat.id, message.chat.first_name+' '+message.chat.last_name)
            if (user.isNew == 1):
                self.bot.send_message(message.chat.id, 'Привет!')
                self.bot.send_message(message.chat.id, 'Добавьте информацию о себе.')
                self.bot.send_message(message.chat.id, 'Мы знакомим участников раз в неделю или чаще.')
                self.startWizard(user, message)
            else:
                self.doneMessage(user, message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def cb(call):
            user = self._dbHelper.getUser(call.from_user.id)    
            self.bot.clear_step_handler(call.message) 
            if (call.data == 'cb_pic'):
                self.picMessage(user, call.message)
            elif (call.data == 'cb_name'):
                self.nameMessage(user, call.message)
            elif (call.data == 'cb_job'):
                self.jobMessage(user, call.message)
            elif (call.data == 'cb_interest'):
                self.interestMessage(user, call.message)
            elif (call.data == 'cb_city'):
                self.cityMessage(user, call.message)
            elif (call.data == 'cb_skill'):
                self.skillMessage(user, call.message)
            elif (call.data == 'cb_pic_from_profile'):
                request = self.bot.get_user_profile_photos(call.from_user.id)
                self.savePic(user, request.photos[0][0].file_id)
                self.nextStep(user, call.message)
            elif (call.data == 'cb_use_profile_name'):
                user.name = call.from_user.first_name+' '+call.from_user.last_name
                self._dbHelper.updUser(user)
                self.nextStep(user, call.message)
            elif ('cb_enable' in call.data):
                buttonPlace = call.data.split(sep='#')
                user.enabled = 1
                self._dbHelper.updUser(user)
                if (buttonPlace[1] == 'done'):
                    markup = self.doneButtons(user)
                elif (buttonPlace[1] == 'profile'):
                    markup = self.profileButtons(user)
                self.bot.edit_message_text(chat_id = call.message.chat.id,
                                            text = call.message.text,
                                            message_id = call.message.message_id,
                                            reply_markup = markup)
                nextMonday = datetime.today() + timedelta(days=(0-datetime.today().weekday()+7)%7)
                self.bot.send_message(user.telegramId, 'Мы вам отправим приглашение '+nextMonday.strftime('%d.%m.%Y'))
            elif ('cb_disable' in call.data):
                buttonPlace = call.data.split(sep='#')
                user.enabled = 0
                self._dbHelper.updUser(user)
                if (buttonPlace[1] == 'done'):
                    markup = self.doneButtons(user)
                elif (buttonPlace[1] == 'profile'):
                    markup = self.profileButtons(user)
                self.bot.edit_message_text(chat_id = call.message.chat.id,
                                            text = call.message.text,
                                            message_id = call.message.message_id,
                                            reply_markup = markup)
                self.bot.send_message(user.telegramId, 'Вы больше не участвуете в нетворкинге, для участия нажмите "Участвовать в нетворкинге"')
            elif (call.data == 'cb_open_profile'):
                self.sendProfile(user, user)
                self.bot.send_message(user.telegramId, 'Что вы хотите добавить или изменить?', reply_markup=self.profileButtons(user))
                                
            elif ('cb_run_cnt#' in call.data):
#call.data format type#runCnt
                runCnt = call.data.split(sep='#')
                user.runCnt = runCnt[1]
                self._dbHelper.updUser(user)
                self.bot.edit_message_text(chat_id = call.message.chat.id,
                                            text = call.message.text,
                                            message_id = call.message.message_id,
                                            reply_markup = None) 
                self.bot.send_message(user.telegramId, 'Сохранено.')
            elif ('cb_check_meet_yes' in call.data):
#call.data format type#pairTelgramId#index
                options = call.data.split(sep='#')
                self._dbHelper.updatePairStatus(call.from_user.id, options[1], 1, (datetime.today()- timedelta(weeks=1)).strftime('%Y%m%d'))
                markup = types.InlineKeyboardMarkup(row_width=1)
                itembtn = [types.InlineKeyboardButton('Встреча состоялась, отличный собеседник!', callback_data='cb_save_opinion#0#0#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Встреча состоялась, не могу сформулировать мнение о собеседнике', callback_data='cb_save_opinion#0#1#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Встреча состоялась, но, к сожалению, не сложилось общение', callback_data='cb_save_opinion#0#2#'+options[1]+'#'+options[2])]
                markup.add(*itembtn)   
                self.bot.send_message(call.from_user.id, 'Отлично. Как вам собеседник?', reply_markup=markup)       
            elif ('cb_check_meet_no' in call.data):
#call.data format type#pairTelgramId#index
                options = call.data.split(sep='#')
                self._dbHelper.updatePairStatus(call.from_user.id, options[1], 0, (datetime.today()- timedelta(weeks=1)).strftime('%Y%m%d'))
                markup = types.InlineKeyboardMarkup(row_width=1)
                itembtn = [types.InlineKeyboardButton('Не было времени, чтобы написать', callback_data='cb_save_opinion#1#0#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Забыл написать', callback_data='cb_save_opinion#1#1#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Собеседник не ответил', callback_data='cb_save_opinion#1#2#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Собеседник не написал', callback_data='cb_save_opinion#1#3#'+options[1]+'#'+options[2]),
                           types.InlineKeyboardButton('Другая причина', callback_data='cb_other_opinion#'+options[1]+'#'+options[2])]
                markup.add(*itembtn)   
                self.bot.send_message(call.from_user.id, 'Почему?', reply_markup=markup)      
            elif ('cb_save_opinion#' in call.data):
#call.data format type#status#opinion#pairTelgramId#index
                options = call.data.split(sep='#')
                print
                self._dbHelper.insOpinion(call.from_user.id, options[3], call.message.reply_markup.keyboard[int(options[2])][0].text)                
                if (options[1] == 1): #cb_check_meet_no
                    self.bot.send_message(call.from_user.id, 'Ясно.')
                    self.bot.send_message(call.from_user.id, 'Надеюсь, в следующий раз все получится! ✊')
                self.checkMeetNext(call.from_user.id, int(options[4]))
            elif ('cb_other_opinion' in call.data):
#call.data format type#pairTelgramId#index
                options = call.data.split(sep='#')
                self.bot.send_message(call.from_user.id, 'Какая?')
                markup = types.InlineKeyboardMarkup(row_width=1)
                itembtn = [types.InlineKeyboardButton('Пропустить', callback_data='cb_opinion_skip#'+options[2])]
                markup.add(*itembtn)   
                self.bot.send_message(call.from_user.id, 'Расскажите, почему не удалось встретиться, или напишите "пропустить", если не хотите ничего указывать.', reply_markup=markup)  
                self.bot.register_next_step_handler(call.message, lambda message: self.saveOpinion(message, options[1], int(options[2])))
            elif ('cb_opinion_skip' in call.data):
#call.data format type#index
                options = call.data.split(sep='#')                
                self.bot.clear_step_handler(call.message)
                self.checkMeetNext(call.from_user.id, int(options[1]))
            elif ('cb_change_type' in call.data):
#call.data format type#user
                options = call.data.split(sep='#')
                changedUser = self._dbHelper.getUser(options[1])
                changedUser.type = 2
                self._dbHelper.updUser(changedUser)
                self.bot.edit_message_text(chat_id = call.message.chat.id,
                                            text = call.message.text,
                                            message_id = call.message.message_id,
                                            reply_markup = None) 
                self.bot.send_message(call.from_user.id, 'Пользователь стал участником проекта.')                
            else:
                raise RuntimeError

# start bot polling                
        threading.Thread(target=self.botThread).start()

    def botThread(self):
        while True:
            self.bot.polling(non_stop=True) 

    def startWizard(self, user, message):
        if (user.wizardStage == 'name'):
            self.nameMessage(user, message)
        elif (user.wizardStage == 'pic'):
            self.picMessage(user, message)
        elif (user.wizardStage == 'job'):
            self.jobMessage(user, message)
        elif (user.wizardStage == 'interest'):
            self.interestMessage(user, message)  
        elif (user.wizardStage == 'city'):
            self.cityMessage(user, message)        
        elif (user.wizardStage == 'skill'):
            self.skillMessage(user, message)        
        elif (user.wizardStage == 'done'):
            user.isNew = 0
            user.wizardStage = None
            self._dbHelper.updUser(user)
            self.doneMessage(user, message)
            self.sendProfileToAdmin(user)


    def nextStep(self, user, message):
        
        self.bot.clear_step_handler(message)
        if (user.wizardStage == 'name'):
            user.wizardStage = 'pic'
        elif (user.wizardStage == 'pic'):
            user.wizardStage = 'job'
        elif (user.wizardStage == 'job'):
            user.wizardStage = 'interest'
        elif (user.wizardStage == 'interest'):
            user.wizardStage = 'city'
        elif (user.wizardStage == 'city'):
            user.wizardStage = 'skill'
        elif (user.wizardStage == 'skill'):
            user.wizardStage = 'done'
        else:
            self.bot.send_message(user.telegramId, 'Сохранено.')
        self._dbHelper.updUser(user)
        self.startWizard(user, message)


    def picMessage(self, user, message):
        request = self.bot.get_user_profile_photos(user.telegramId)
        profileText = ''
        if (len(request.photos) > 0):
            if (len(request.photos[0]) > 0):
                if (len(request.photos[0][0].file_id) != None):
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Из профиля', callback_data='cb_pic_from_profile'))
                    profileText = 'В вашем профиле уже есть фото. Нажмите "Из профиля" и я возьму его.'
        self.bot.send_message(user.telegramId, 'Загрузите свое фото, чтобы люди знали, как вы выглядите. ' \
                                          'Можно прислать уже сделанное фото, но я рекомендую сделать селфи прямо сейчас. '\
                                          'Так вас легче будет узнать. Отправьте свое фото прямо сюда. '\
                                          + profileText, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.loadPic)
    def nameMessage(self, user, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Использовать {0:s} {1:s}'.format(message.chat.first_name, message.chat.last_name), callback_data='cb_use_profile_name'))
        self.bot.send_message(user.telegramId, 'Как вас представлять другим участникам? В вашем профиле указано, что ваше имя - {0:s} {1:s}.'\
                                               'Я могу использовать его. Или пришлите мне свое имя текстом.'.format(message.chat.first_name, message.chat.last_name), reply_markup=markup)
        self.bot.register_next_step_handler(message, self.saveName)
    def jobMessage(self, user, message):
        self.bot.send_message(user.telegramId, 'Где и кем вы работаете? Это поможет людям понять, чем вы можете быть интересны. '\
                                               'Пришлите мне, пожалуйста, название компании и вашу должность. Например, "Директор в "ООО Палехче".')
        self.bot.register_next_step_handler(message, self.saveJob)
    def interestMessage(self, user, message):
        self.bot.send_message(user.telegramId, 'О каких темах вам было бы интересно поговорить? '\
                                               'Например, "инвестиции, советы по воспитанию детей, возможна ли медицина в условиях невесомости".')
        self.bot.register_next_step_handler(message, self.saveInterest)
    def cityMessage(self, user, message):
        self.bot.send_message(user.telegramId, 'В каком городе проживаете? Например, "Уфа".')
        self.bot.register_next_step_handler(message, self.saveCity)
    def skillMessage(self, user, message):
        self.bot.send_message(user.telegramId, 'В каких темах вы разбираетест? Например, "умею пасти котов, инвестирую, развожу сурков".')
        self.bot.register_next_step_handler(message, self.saveSkill)

    def doneButtons(self, user):
        markup = types.InlineKeyboardMarkup()
        if (user.isFull() == 1 and user.enabled == 0):
            markup.add(types.InlineKeyboardButton('Участвовать в нетворкинге', callback_data='cb_enable#done'))
        markup.add(types.InlineKeyboardButton('Профиль', callback_data='cb_open_profile'))
        return markup
    def doneMessage(self, user, message):
        enableText = ''
        if (user.isFull() == 1 and user.enabled == 0):
            enableText = ' Нажмите "Участвовать в нетворкинге" для получения информации об участниках'
        self.bot.send_message(user.telegramId, 'Профиль заполнен.'+enableText, reply_markup=self.doneButtons(user))
        self.bot.register_next_step_handler(message, self.saveName)

    def profileButtons(self, user):
        markup = types.InlineKeyboardMarkup(row_width=2)
        itembtn = [types.InlineKeyboardButton('Фото', callback_data='cb_pic'),
                   types.InlineKeyboardButton('Имя и Фамилия', callback_data='cb_name'),
                   types.InlineKeyboardButton('Компания и позиция', callback_data='cb_job'),
                   types.InlineKeyboardButton('Что я ищу', callback_data='cb_interest'),
                   types.InlineKeyboardButton('Город', callback_data='cb_city'),
                   types.InlineKeyboardButton('Чем могу быть полезен', callback_data='cb_skill')]
        markup.add(*itembtn)     
        if (user.isFull() == 1):
            if (user.enabled == 0): 
                markup.add(types.InlineKeyboardButton('Участвовать в нетворкинге', callback_data='cb_enable#profile'))     
            elif (user.enabled == 1): 
                markup.add(types.InlineKeyboardButton('Не участвовать в нетворкинге', callback_data='cb_disable#profile'))     
        return markup
    

    def loadPic(self, message):
        if (message.content_type != 'photo'):
            self.bot.send_message(message.chat.id, 'Неоходимо загрузить фото!')
            self.bot.register_next_step_handler(message, self.loadPic)   
            return
        user = self._dbHelper.getUser(message.chat.id)
        self.savePic(user, message.photo[-1].file_id)        
        self.nextStep(user, message)
     
    def savePic(self, user, fileId):
        fileInfo = self.bot.get_file(fileId)
        downloadedFile = self.bot.download_file(fileInfo.file_path)
        fileName = 'img/'+str(user.telegramId)+'.jpg'
        print(fileName)
        with open(fileName, 'wb') as newFile:
            newFile.write(downloadedFile)     
        user.pic = fileName
        self._dbHelper.updUser(user)

    def saveName(self, message):
        user = self._dbHelper.getUser(message.chat.id)    
        user.name = message.text
        self._dbHelper.updUser(user)  
        self.nextStep(user, message)
    def saveJob(self, message):
        user = self._dbHelper.getUser(message.chat.id)    
        user.job = message.text
        self._dbHelper.updUser(user) 
        self.nextStep(user, message)
    def saveInterest(self, message):
        user = self._dbHelper.getUser(message.chat.id)    
        user.interest = message.text
        self._dbHelper.updUser(user)  
        self.nextStep(user, message)
    def saveCity(self, message):
        user = self._dbHelper.getUser(message.chat.id)    
        user.city = message.text
        self._dbHelper.updUser(user) 
        self.nextStep(user, message)
    def saveSkill(self, message):
        user = self._dbHelper.getUser(message.chat.id)    
        user.skill = message.text
        self._dbHelper.updUser(user)  
        self.nextStep(user, message)

    def sendProfile(self, user, profileUser, additionalMessage = None):
        self.bot.send_photo(user.telegramId, photo=open(profileUser.pic, 'rb'))
        message = profileUser.name + ' ' + profileUser.job + '\nЯ ищу: '+profileUser.interest+'\nГород: '+profileUser.city+'\nМогу быть полезен: '+profileUser.skill

        if (profileUser.type == 1):
            message += '\nТип профиля: интересующийся.'
        elif (profileUser.type == 2):
            message += '\nТип профиля: участник проекта.'
        if (additionalMessage != None):
            message = message+'\n'+additionalMessage
        self.bot.send_message(user.telegramId, message, parse_mode='HTML')

    def saveOpinion(self, message, pairTelgramId, listIndex):
        self._dbHelper.insOpinion(message.chat.id, pairTelgramId, message.text) 
        self.checkMeetNext(message.chat.id, listIndex)        

    def askRunCnt(self, user):
        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtn = [types.InlineKeyboardButton('Участвую один раз', callback_data='cb_run_cnt#1'),
                   types.InlineKeyboardButton('Участвую два раза', callback_data='cb_run_cnt#2'),
                   types.InlineKeyboardButton('Участвую три раза', callback_data='cb_run_cnt#3')]
        markup.add(*itembtn)       
        self.bot.send_message(user.telegramId, 'Сколько раз хотите участвовать на этой неделе?', reply_markup=markup)

    def sendPair(self, user):
        self.bot.send_message(user.telegramId, 'Привет!👋')
        if (len(user.currentPairs) > 1):
            self.bot.send_message(user.telegramId, 'Ваши пары на сегодня:')
        else:
            self.bot.send_message(user.telegramId, 'Ваша пара на сегодня:')
        for pairUser in user.currentPairs:
            additionalMessage = 'Напишите партнеру в Telegram: <a href="tg://user?id={0:s}">{1:s}</a>'.format(str(pairUser.telegramId), pairUser.name) + '\n\nНе откладывайте, договорись о встрече сразу'
            self.sendProfile(user, pairUser, additionalMessage)


    def sendReminder(self, telegramId):
        self.bot.send_message(telegramId, 'Напишите своему партнеру, если вдруг забыли.')

    def newUserReminder(self, user):
        self.bot.send_message(user.telegramId, 'Ваш профиль не полон.')
        message = self.bot.send_message(user.telegramId, 'Ответь, пожалуйста, на несколько вопросов о себе, чтобы бот смог подобрать вам пару.')
        self.startWizard(user, message)

    def checkMeet(self, telegramId, pairUserList, listIndex):
        if (len(pairUserList) == listIndex):
            self.bot.send_message(telegramId, 'Спасибо за ответы')
            return
        if (listIndex == 0):
            self.bot.send_message(telegramId, 'Небольшой опрос.')
        markup = types.InlineKeyboardMarkup(row_width=2)
        itembtn = [types.InlineKeyboardButton('Встреча состоялась', callback_data='cb_check_meet_yes#'+str(pairUserList[listIndex].telegramId)+'#'+str(listIndex)),
                   types.InlineKeyboardButton('Не получилось встретиться', callback_data='cb_check_meet_no#'+str(pairUserList[listIndex].telegramId)+'#'+str(listIndex))]
        markup.add(*itembtn)   
        self.bot.send_message(telegramId, 'Состоялась встреча c {0:s}?'.format(pairUserList[listIndex].name), reply_markup=markup)

    def checkMeetNext(self, telegramId, listIndex):
        pairUserList = self._dbHelper.getPairsByUser(telegramId, (datetime.today()- timedelta(weeks=1)).strftime('%Y%m%d'))
        self.checkMeet(telegramId, pairUserList, listIndex+1)

    def sendProfileToAdmin(self, user):
        adminUserList = self._dbHelper.getAdminUsers()
        for adminUser in adminUserList:
            self.sendProfile(adminUser, user)
            if (user.type == 1):
                markup = types.InlineKeyboardMarkup(row_width=2)
                itembtn = types.InlineKeyboardButton('Участник проекта', callback_data='cb_change_type#'+str(user.telegramId))
                markup.add(itembtn) 
                self.bot.send_message(adminUser.telegramId, 'Сделать участником проекта?', reply_markup=markup)

            