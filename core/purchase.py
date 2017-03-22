# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-02 17:25
Description:

"""
import json
import hashlib

import arrow
import requests

from django.db.models import Q
from django.conf import settings

from dianjing.exception import GameException

from apps.character.models import Character as ModelCharacter
from apps.purchase.models import (
    Purchase as ModelPurchase,
    Purchase1SDK as ModelPurchase1SDK,
    PurchaseIOS as ModelPurchaseIOS,
    PurchaseStarsCloud as ModelPurchaseStarsCloud,
)

from core.mongo import MongoPurchase, MongoPurchaseLog
from core.resource import ResourceClassification, money_text_to_item_id, VIP_EXP_ITEM_ID
from core.mail import MailManager
from core.signals import purchase_done_signal

from utils.message import MessagePipe
from utils.functional import make_string_id, get_start_time_of_today

from config import ConfigPurchaseYueka, ConfigPurchaseGoods, ConfigErrorMessage, ConfigPurchaseFirstReward

from protomsg.purchase_pb2 import (
    PurchaseNotify,
    PURCHASE_DONE,
    PURCHASE_FAILURE,
    PURCHASE_WAITING,
)

YUEKA_ID = 1001

IOS_VERIFY_URL = 'https://buy.itunes.apple.com/verifyReceipt'
IOS_VERIFY_URL_TEST = 'https://sandbox.itunes.apple.com/verifyReceipt'

IOS_PRODUCT_ID_TO_GOODS_ID_TABLE = {
    ConfigPurchaseYueka.get(YUEKA_ID).ios_product_id: YUEKA_ID
}

for k, v in ConfigPurchaseGoods.INSTANCES.iteritems():
    IOS_PRODUCT_ID_TO_GOODS_ID_TABLE[v.ios_product_id] = k


def get_fee(goods_id):
    if goods_id == YUEKA_ID:
        return ConfigPurchaseYueka.get(YUEKA_ID).rmb
    return ConfigPurchaseGoods.get(goods_id).rmb


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

        condition = {'$and': [
            {'yueka_remained_days': {'$gt': 0}},
            {'yueka_new': False}
        ]}

        docs = MongoPurchase.db(server_id).find(condition)
        MongoPurchase.db(server_id).update_many(
            condition,
            {'$inc': {
                'yueka_remained_days': -1
            }}
        )

        # 把今天新购买的，设置为False,以便后面的定时任务好发送月卡
        MongoPurchase.db(server_id).update_many(
            {'yueka_new': True},
            {'$set': {'yueka_new': False}}
        )

        rc = ResourceClassification.classify(config.rewards)
        attachment = rc.to_json()

        amount = 0
        for doc in docs:
            m = MailManager(server_id, doc['_id'])
            m.add(config.mail_title, config.mail_content, attachment=attachment)
            amount += 1

        return amount



    def verify_ios(self, param):
        def _do_error_record(_status):
            ModelPurchaseIOS.objects.create(
                id=make_string_id(),
                transaction_id='',
                product_id='',
                quantity=0,
                status=_status,
                environment='',
                application_version='',
                receipt_data=param
            )

        res = verify_ios(param)
        if not res:
            _do_error_record(-1)
            return 0, PURCHASE_FAILURE

        status = res['status']
        if status != 0:
            _do_error_record(status)
            return 0, PURCHASE_FAILURE

        environment = res['environment']
        application_version = res['receipt']['application_version']

        in_app = res['receipt']['in_app'][-1]
        product_id = in_app['product_id']
        quantity = int(in_app['quantity'])
        transaction_id = in_app['transaction_id']

        this_record = ModelPurchaseIOS.objects.filter(transaction_id=transaction_id)
        if this_record.exists():
            pid = this_record.first().id
            pobj = ModelPurchase.objects.get(id=pid)
            return pobj.goods_id, PURCHASE_DONE

        goods_id = IOS_PRODUCT_ID_TO_GOODS_ID_TABLE[product_id]

        _id = self.record('ios', goods_id, amount=quantity)

        ModelPurchaseIOS.objects.create(
            id=_id,
            transaction_id=transaction_id,
            product_id=product_id,
            quantity=quantity,
            status=0,
            environment=environment,
            application_version=application_version,
            receipt_data=param
        )

        self.send_reward(goods_id)
        return goods_id, PURCHASE_DONE

    # TODO verify 代码可以优化
    def verify_other(self, param):
        condition = Q(char_id=self.char_id) & Q(verified=False)
        query = ModelPurchase.objects.filter(condition).order_by('-create_at')
        if query.count() == 0:
            return 0, PURCHASE_WAITING

        p = query.first()
        """:type: ModelPurchase"""

        if p.platform == '1sdk':
            status = verify_1sdk(p.id)
        elif p.platform == 'stars-cloud':
            status = PURCHASE_DONE
        else:
            raise RuntimeError("Platform {0} NOT support!".format(p.platform))

        if status == PURCHASE_DONE:
            p.verified = True
            p.save()

        return p.goods_id, status

    def get_purchase_times(self):
        # 充值次数
        return MongoPurchaseLog.db(self.server_id).find({'char_id': self.char_id}).count()

    def get_purchase_info_of_day_shift(self, days=0):
        today = get_start_time_of_today()
        start = today.replace(days=days)
        end = start.replace(days=1)
        return self._get_purchase_info(start.timestamp, end.timestamp)

    def get_purchase_info_of_date(self, date):
        start = date
        end = start.replace(days=1)
        return self._get_purchase_info(start.timestamp, end.timestamp)

    def _get_purchase_info(self, start_timestamp, end_timestamp):
        info = []
        condition = {'$and': [
            {'char_id': self.char_id},
            {'timestamp': {'$gte': start_timestamp}},
            {'timestamp': {'$lt': end_timestamp}}
        ]}

        docs = MongoPurchaseLog.db(self.server_id).find_one(condition)
        for doc in docs:
            info.append((doc['goods_id'], doc['actual_got']))

        return info

    def get_first_reward(self):
        if self.get_purchase_times() == 0:
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_NOT_FIRST_REWARD"))

        if self.doc.get('first_reward_got', False):
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_FIRST_REWARD_HAS_GOT"))

        drop = ConfigPurchaseFirstReward.get_reward()
        rc = ResourceClassification.classify(drop)
        rc.add(self.server_id, self.char_id, message="Purchase.get_first_reward")
        self.doc['first_reward_got'] = True

        MongoPurchase.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'first_reward_got': True
            }}
        )

        self.send_notify()
        return rc

    def record(self, platform, goods_id, amount=1):
        _id = make_string_id()
        fee = get_fee(goods_id) * amount

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
            # 月卡买了就立即发送
            # 后面的再定时发送
            config = ConfigPurchaseYueka.get(YUEKA_ID)
            got = 0
            actual_got = 0

            MongoPurchase.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'yueka_remained_days': 29,
                    'yueka_new': True
                }}
            )

            self.doc['yueka_remained_days'] = 29
            self.doc['yueka_new'] = True

            rc = ResourceClassification.classify(config.rewards)
            attachment = rc.to_json()

            m = MailManager(self.server_id, self.char_id)
            m.add(config.mail_title, config.mail_content, attachment=attachment)
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
        rc.add(self.server_id, self.char_id, message="Purchase.send_reward:{0}".format(goods_id))

        purchase_done_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            goods_id=goods_id,
            got=got,
            actual_got=actual_got,
        )

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


def verify_ios(receipt):
    data = json.dumps({
        'receipt-data': receipt
    })

    def _do(url):
        try:
            req = requests.post(url, data=data, timeout=10)
            assert req.ok
        except Exception as e:
            print "==== IOS VERIFY ERROR ===="
            print e
            raise e

        return req.json()

    try:
        res = _do(IOS_VERIFY_URL)
    except:
        return None

    if res['status'] == 21007:
        # 测试的交易凭证，却发到了正式服务器去验证
        try:
            res = _do(IOS_VERIFY_URL_TEST)
        except:
            return None

    return res


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
    _id = p.record('1sdk', goods_id)

    # 记录下来
    ModelPurchase1SDK.objects.create(
        id=_id,
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


def platform_callback_stars_cloud(params):
    print "<< PLATFORM CALLBACK STARS-CLOUD >>"
    print params

    tp = params['type']
    if tp != 'pay':
        return 'ok'

    amount = params['amount']  # 金额 分
    channOrderId = params['channOrderId']
    channType = params['channType']
    pmOrderId = params['pmOrderId']
    uid = params['uid']
    pmAppId = params['pmAppId']
    extraInfo = params['extraInfo']
    sign = params['sign']

    if ModelPurchaseStarsCloud.objects.filter(pmOrderId=pmOrderId).exists():
        return 'ok'

    pmSecret = settings.THIRD_PROVIDER['stars-cloud']['pmsecret']

    text = "amount={0}&channOrderId={1}&channType={2}&pmOrderId={3}&uid={4}&pmAppId={5}&pmSecret={6}".format(
        amount, channOrderId, channType, pmOrderId, uid, pmAppId, pmSecret
    )

    result = hashlib.md5(text).hexdigest()
    if result != sign:
        print "<< PLATFORM CALLBACK STARS-CLOUD >>"
        print "sign not match"
        return 'fail'

    char_id, goods_id = extraInfo.split(',')
    char_id = int(char_id)
    goods_id = int(goods_id)

    try:
        c = ModelCharacter.objects.get(id=char_id)
    except ModelCharacter.DoesNotExist:
        print "<< PLATFORM CALLBACK STARS-CLOUD >>"
        print "char id not found. {0}".format(char_id)
        return 'fail'

    if goods_id != YUEKA_ID and not ConfigPurchaseGoods.get(goods_id):
        print "<< PLATFORM CALLBACK STARS-CLOUD >>"
        print "goods id not found. {0}".format(goods_id)
        return 'fail'

    p = Purchase(c.server_id, char_id)
    _id = p.record('stars-cloud', goods_id)

    ModelPurchaseStarsCloud.objects.create(
        id=_id,
        amount=int(amount),
        channOrderId=channOrderId,
        channType=channType,
        pmOrderId=pmOrderId,
        uid=uid
    )

    p.send_reward(goods_id)
    return 'ok'
