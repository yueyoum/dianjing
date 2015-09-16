import re

from apps.server.models import Server

from core.db import MongoDB


# Create your models here.


def get_servers():
    return Server.opened_servers()


class DBHandle(object):
    def __init__(self, server_id):
        self.server_id = server_id
        self.mongo = MongoDB.get(server_id)

    def get_data(self, tp, text):
        data = {}
        if tp == 'id' and re.match(r'[1-9][0-9]*$', text):
            data['char'] = self.mongo.character.find_one({'_id': int(text)})
        elif tp == 'name':
            data['char'] = self.mongo.character.find_one({'name': text})
        elif tp == 'club':
            data['char'] = self.mongo.character.find_one({'club.name': text})
        else:
            return None

        if data['char'] == None:
            return None
        data['friend'] = self.mongo.friend.find_one({'_id': data['char']['_id']})

        data['building'] = self.mongo.building.find_one({'_id': data['char']['_id']})

        data['mail'] = self.mongo.mail.find_one({'_id': data['char']['_id']})

        data['staff'] = self.mongo.staff.find_one({'_id': data['char']['_id']})

        return data
