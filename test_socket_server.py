# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_socket_server
Date Created:   2016-09-20 17:06
Description:

"""

import socket
import threading

from utils.message import MessageFactory, NUM_FILED
from utils.session import GameSession

from protomsg import ID_TO_MESSAGE

from protomsg.arena_pb2 import *
from protomsg.activity_pb2 import *
from protomsg.account_pb2 import *

from protomsg.broadcast_pb2 import *
from protomsg.bag_pb2 import *

from protomsg.club_pb2 import *
from protomsg.common_pb2 import *
from protomsg.challenge_pb2 import *
from protomsg.chat_pb2 import *
from protomsg.collection_pb2 import *

from protomsg.dungeon_pb2 import *

from protomsg.energy_pb2 import *

from protomsg.formation_pb2 import *
from protomsg.friend_pb2 import *

from protomsg.mail_pb2 import *
from protomsg.match_pb2 import *

from protomsg.notification_pb2 import *

from protomsg.party_pb2 import *
from protomsg.package_pb2 import *
from protomsg.plunder_pb2 import *
from protomsg.purchase_pb2 import *

from protomsg.resource_pb2 import *

from protomsg.server_pb2 import *
from protomsg.staff_pb2 import *
from protomsg.statistics_pb2 import *
from protomsg.store_pb2 import *

from protomsg.talent_pb2 import *
from protomsg.task_pb2 import *
from protomsg.territory_pb2 import *
from protomsg.tower_pb2 import *

from protomsg.union_pb2 import *
from protomsg.unit_pb2 import *

from protomsg.vip_pb2 import *

from protomsg.welfare_pb2 import *

g = globals()


def recv(s):
    while True:
        head = s.recv(4)
        if not head:
            print "lose connection"
            break

        length = NUM_FILED.unpack(head)[0]

        data = s.recv(length)

        msg_id = NUM_FILED.unpack(data[:4])[0]
        print "MSG ID:", msg_id
        msg_name = ID_TO_MESSAGE[msg_id]
        print "MSG NAME:", msg_name

        msg = g[msg_name]()
        msg.ParseFromString(data[4:])

        print msg

class Client(object):
    def __init__(self, account_id, server_id, char_id):
        self.account_id = account_id
        self.server_id = server_id
        self.char_id = char_id

        self.s = None

    def connect(self, host="121.42.152.158", port=7999):
        self.s = socket.socket()
        self.s.connect((host, port))

        t = threading.Thread(target=recv, args=[self.s])
        t.daemon = True
        t.start()

    def _send(self, msg):
        data = MessageFactory.pack(msg)
        self.s.sendall(data)

    def send_socket_connect_request(self):
        msg = SocketConnectRequest()
        msg.session = GameSession.dumps(account_id=self.account_id,
                                        server_id=self.server_id,
                                        char_id=self.char_id)

        self._send(msg)

    def get_room_list(self):
        msg = PartyRoomRequest()
        self._send(msg)

    def party_create(self):
        msg = PartyCreateRequest()
        msg.id = 1
        self._send(msg)

    def party_join(self, owner_id):
        msg = PartyJoinRequest()
        msg.owner_id = str(owner_id)
        self._send(msg)

    def party_quit(self):
        msg = PartyQuitRequest()
        self._send(msg)

    def party_kick(self, target_id):
        msg = PartyKickRequest()
        msg.id = str(target_id)
        self._send(msg)

    def party_chat(self, text):
        msg = PartyChatRequest()
        msg.text = text
        self._send(msg)

    def party_buy(self, buy_id):
        msg = PartyBuyRequest()
        msg.buy_id = buy_id
        self._send(msg)

    def party_start(self):
        msg = PartyStartRequest()
        self._send(msg)

    def party_dismiss(self):
        msg = PartyDismissRequest()
        self._send(msg)
