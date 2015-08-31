

from apps.server.models import Server

from core.db import MongoDB

# Create your models here.


def get_servers():
    return Server.opened_servers()


class DBHandle(object):
    def __init__(self, server_id):
        self.server_id = server_id
        self.mongo = MongoDB.get(server_id)

    def get_collections(self):
        collections = self.mongo.collection_names()
        names = []
        for k in collections:
            if k != 'system.indexes' and k != 'server':
                names.append(k)
        return names

    def get_building(self):
        return self.mongo.building.find()

    def get_char(self):
        return self.mongo.character.find()

    def get_club(self, char_id):
        return self.mongo.character.find_one({'_id': char_id}, {'club': 1})

    def get_common(self):
        return self.mongo.common.find()

    def get_friend(self):
        return self.mongo.friend.find()

    def get_league_event(self):
        return self.mongo.league_event.find()

    def get_league_group(self):
        return self.mongo.league_group.find()

    def get_mail(self):
        return self.mongo.mail.find()

    def get_mail_one(self, char_id, mail_id):
        mails = self.mongo.mail.find_one({'_id': char_id})
        return mails

    def get_staff(self):
        return self.mongo.staff.find()

    def get_char_staff(self, char_id):
        return self.mongo.staff.find_one({'_id': char_id}, {'staffs': 1})

    def get_recruit(self):
        return self.mongo.recruit.find()

    def get_training_store(self):
        return self.mongo.training_store.find()
