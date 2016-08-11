# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-02 17:25
Description:

"""
import hashlib
import arrow

from django.db.models import Q

from dianjing.exception import GameException

from apps.character.models import Character as ModelCharacter
from apps.purchase.models import (
    Purchase as ModelPurchase,
    Purchase1SDK as ModelPurchase1SDK,
)

from core.mongo import MongoPurchase, MongoPurchaseLog
from core.resource import ResourceClassification, money_text_to_item_id, VIP_EXP_ITEM_ID
from core.mail import MailManager

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import ConfigPurchaseYueka, ConfigPurchaseGoods, ConfigErrorMessage, ConfigPurchaseFirstReward

from protomsg.purchase_pb2 import PurchaseNotify, PURCHASE_DONE, PURCHASE_FAILURE, PURCHASE_WAITING

YUEKA_ID = 1001


class Purchase(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoPurchase.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoPurchase.document()
            self.doc['_id'] = self.char_id
            MongoPurchase.db(self.server_id).insert_one(self.doc)

    @classmethod
    def send_yueka_reward(cls, server_id):
        config = ConfigPurchaseYueka.get(YUEKA_ID)

        docs = MongoPurchase.db(server_id).find({'yueka_remained_days': {'$gt': 0}})
        MongoPurchase.db(server_id).update_many(
            {'yueka_remained_days': {'$gt': 0}},
            {'$inc': {
                'yueka_remained_days': -1
            }}
        )

        rc = ResourceClassification.classify(config.rewards)
        attachment = rc.to_json()

        amount = 0
        for doc in docs:
            m = MailManager(server_id, doc['_id'])
            m.add(config.mail_title, config.mail_content, attachment=attachment)
            amount += 1

        return amount

    def verify(self, param):
        condition = Q(char_id=self.char_id) & Q(verified=False)
        query = ModelPurchase.objects.filter(condition).order_by('-create_at')
        if query.count() == 0:
            return 0, PURCHASE_WAITING

        p = query.first()
        """:type: ModelPurchase"""

        if p.platform == '1sdk':
            status = verify_1sdk(p.id)
        else:
            raise RuntimeError("Platform {0} NOT support!".format(p.platform))

        if status == PURCHASE_DONE:
            p.verified = True
            p.save()

        return p.goods_id, status

    def get_purchase_times(self):
        # 充值次数
        return MongoPurchaseLog.db(self.server_id).find({'char_id': self.char_id}).count()

    def get_first_reward(self):
        if self.get_purchase_times() != 1:
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_NOT_FIRST_REWARD"))

        if self.doc.get('first_reward_got', False):
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_FIRST_REWARD_HAS_GOT"))

        drop = ConfigPurchaseFirstReward.get_reward()
        rc = ResourceClassification.classify(drop)
        rc.add(self.server_id, self.char_id)
        self.doc['first_reward_got'] = True

        MongoPurchase.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'first_reward_got': True
            }}
        )

        self.send_notify()
        return rc

    def record(self, goods_id, platform, fee):
        _id = make_string_id()
        ModelPurchase.objects.create(
            id=_id,
            server_id=self.server_id,
            char_id=self.char_id,
            goods_id=goods_id,
            platform=platform,
            fee=fee,
            verified=False,
        )

        return _id

    def send_reward(self, goods_id):
        if goods_id == YUEKA_ID:
            config = ConfigPurchaseYueka.get(YUEKA_ID)
            got = 0
            actual_got = 0

            MongoPurchase.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'yueka_remained_days': 30
                }}
            )

            self.doc['yueka_remained_days'] = 30
        else:
            config = ConfigPurchaseGoods.get(goods_id)

            got = config.diamond
            actual_got = config.diamond + config.diamond_extra
            if self.get_purchase_times() == 0:
                # 首充
                actual_got = config.diamond * 2 + config.diamond_extra

        doc = MongoPurchaseLog.document()
        doc['_id'] = make_string_id()
        doc['char_id'] = self.char_id
        doc['goods_id'] = goods_id
        doc['got'] = got
        doc['actual_got'] = actual_got
        doc['timestamp'] = arrow.utcnow().timestamp
        MongoPurchaseLog.db(self.server_id).insert_one(doc)

        reward = [
            (VIP_EXP_ITEM_ID, config.vip_exp),
            (money_text_to_item_id('diamond'), actual_got)
        ]

        rc = ResourceClassification.classify(reward)
        rc.add(self.server_id, self.char_id)

        self.send_notify()

    def send_notify(self):
        notify = PurchaseNotify()
        notify.yueka_remained_days = self.doc['yueka_remained_days']
        notify.first = self.get_purchase_times() == 0

        for _id, _amount in ConfigPurchaseFirstReward.get_reward():
            reward = notify.frist_reward.items.add()
            reward.id = _id
            reward.amount = _amount

        notify.first_reward_got = self.doc.get('first_reward_got', False)
        MessagePipe(self.char_id).put(msg=notify)


def verify_1sdk(order_id):
    try:
        record = ModelPurchase1SDK.objects.get(id=order_id)
        """:type: ModelPurchase1SDK"""
    except ModelPurchase1SDK.DoesNotExist:
        return PURCHASE_WAITING

    if record.st == 1:
        return PURCHASE_DONE

    return PURCHASE_FAILURE


KEY_1SDK = 'II1KEJPVONHA4OB3LV3KOO4G8CFAV3RL'
APPID = 'e15e4e08795db177'


def platform_callback_1sdk(params):
    print "<< PLATFORM CALLBACK 1SDK >>"
    print params

    app = params.get('app', '')
    # cbi 就是自定义参数  char_id,goods_id
    cbi = params.get('cbi', '')
    ct = params.get('ct', '')
    fee = params.get('fee', '')
    pt = params.get('pt', '')
    sdk = params.get('sdk', '')

    ssid = params.get('ssid', '')
    st = params.get('st', '')

    tcd = params.get('tcd', '')

    uid = params.get('uid', '')
    ver = params.get('ver', '')
    sign = params.get('sign', '')

    if app != APPID:
        print "<< PLATFORM CALLBACK 1SDK >>"
        print "app not match. {0}, {1}".format(app, APPID)
        return 'APP NOT MATCH'

    if ModelPurchase1SDK.objects.filter(tcd=tcd).exists():
        return 'SUCCESS'

    check_params = {
        'app': app,
        'cbi': cbi,
        'ct': ct,
        'fee': fee,
        'pt': pt,
        'sdk': sdk,
        'ssid': ssid,
        'st': st,
        'tcd': tcd,
        'uid': uid,
        'ver': ver,
    }

    check_params = ['{0}={1}'.format(k, v) for k, v in check_params.iteritems()]
    check_params.sort()
    check_params = '&'.join(check_params)

    x = hashlib.md5(check_params + KEY_1SDK).hexdigest()
    if x != sign:
        print "<< PLATFORM CALLBACK 1SDK >>"
        print "sign not match. {0}".format(check_params)
        return 'SIGN NOT MATCH'

    char_id, goods_id = cbi.split(',')
    char_id = int(char_id)
    goods_id = int(goods_id)

    try:
        c = ModelCharacter.objects.get(id=char_id)
    except ModelCharacter.DoesNotExist:
        print "<< PLATFORM CALLBACK 1SDK >>"
        print "char id not found. {0}".format(char_id)
        return 'CHAR NOT FOUND'

    if goods_id != YUEKA_ID and not ConfigPurchaseGoods.get(goods_id):
        print "<< PLATFORM CALLBACK 1SDK >>"
        print "goods id not found. {0}".format(goods_id)
        return 'GOODS NOT FOUND'

    p = Purchase(c.server_id, char_id)
    p.record(goods_id, '1sdk', int(fee))

    # 记录下来
    ModelPurchase1SDK.objects.create(
        id=cbi,
        ct=int(ct) / 1000,
        fee=int(fee),
        pt=int(pt) / 1000,
        sdk=sdk,
        ssid=ssid,
        st=int(st),
        tcd=tcd,
        uid=uid,
    )

    p.send_reward(goods_id)
    return 'SUCCESS'
