import re

from apps.server.models import Server

from core.mongo import MongoCharacter, MongoFriend, MongoBuilding, MongoStaff, MongoMail, MongoTraining, MongoTask, MongoLadder


# Create your models here.


def get_servers():
    return Server.opened_servers()


class DBHandle(object):
    def __init__(self, server_id):
        self.server_id = server_id

    def get_char(self, tp, text):
        data = {}
        if tp == 'id' and re.match(r'[1-9][0-9]*$', text):
            data['char'] = MongoCharacter.db(self.server_id).find_one({'_id': int(text)})
        elif tp == 'name':
            data['char'] = MongoCharacter.db(self.server_id).find_one({'name': text})
        elif tp == 'club':
            data['char'] = MongoCharacter.db(self.server_id).find_one({'club.name': text})
        else:
            return None

        if data['char'] == None:
            return None

        data['building'] = MongoBuilding.db(self.server_id).find_one({'_id': data['char']['_id']})
        # data['friend'] = MongoFriend.db(self.server_id).find_one({'_id': data['char']['_id']})
        data['task'] = MongoTask.db(self.server_id).find_one({'_id': data['char']['_id']})

        return data

    def get_staff(self, char_id):
        return MongoStaff.db(self.server_id).find_one({'_id': char_id})

    def get_friend(self, char_id):
        return MongoFriend.db(self.server_id).find_one({'_id': char_id})

    def get_mail(self, char_id):
        return MongoMail.db(self.server_id).find_one({'_id': char_id})

    def get_one_mail(self, char_id, mail_id):
        data = {}
        mails = MongoMail.db(self.server_id).find_one({'_id': char_id})
        data['mail'] = mails["mails"][mail_id]
        data['id'] = char_id
        data['key'] = mail_id
        return data

    def get_knapsack(self, char_id):
        return MongoTraining.db(self.server_id).find_one({'_id': char_id})

    def get_task(self, char_id):
        return MongoTask.db(self.server_id).find_one({'_id': char_id})

    def get_ladder(self):
        return MongoLadder.db(self.server_id).find({'order': {'$lt': 51}}).sort('order', 1)

    def get_club(self, char_id):
        return MongoCharacter.db(self.server_id).find_one({'_id': int(char_id)})


