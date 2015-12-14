# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       resource
Date Created:   2015-07-21 10:17
Description:

"""

from contextlib import contextmanager
from dianjing.exception import GameException

from core.statistics import FinanceStatistics

from config import ConfigErrorMessage


class Resource(object):
    """
        资源检测
    """
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def save_drop(self, drop, message=""):
        """
        掉落资源添加
            1 import 相关模块
            2 如果有俱乐部资源 提取 club_data, update
                2.1 如果有 diamond 或 gold 添加, 写入财务报表 FinanceStatistics
            3 如果有天梯积分 Ladder.add()
            4 如果有训练包 BagTrainingSkill.add()
            5 如果有物品 BagItem.add()

        :type drop: core.package.Drop
        """
        from core.club import Club
        from core.ladder import Ladder
        from core.bag import BagItem, BagTrainingSkill

        if drop.club_renown or drop.gold or drop.diamond:
            club_data = {
                'renown': drop.club_renown,
                'gold': drop.gold,
                'diamond': drop.diamond,
            }

            club = Club(self.server_id, self.char_id)
            club.update(**club_data)

            if drop.gold or drop.diamond:
                FinanceStatistics(self.server_id, self.char_id).add_log(
                    gold=drop.gold, diamond=drop.diamond, message=message
                )

        if drop.ladder_score:
            Ladder(self.server_id, self.char_id).add_score(drop.ladder_score)

        # TODO drop.league_score ?

        if drop.trainings:
            BagTrainingSkill(self.server_id, self.char_id).add(drop.trainings)
        if drop.items:
            BagItem(self.server_id, self.char_id).add(drop.items)

    @contextmanager
    def check(self, **kwargs):
        """
        资源检查
            1 获取解析后数据
            2 预检查(资源是否足够)
            3 扣除资源
            4 如果有 diamond 或 gold 变更, 写入财务系统 FinanceStatistics
        """
        message = kwargs.pop("message", "")
        data = self.data_analysis(**kwargs)
        check_list = self._pre_check_list(data)

        yield

        self._post_check(check_list)

        if data['gold'] or data['diamond']:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                gold=data['gold'],
                diamond=data['diamond'],
                message=message
            )

    @staticmethod
    def data_analysis(**kwargs):
        """
        解析数据
        """
        data = {
            'gold': kwargs.get('gold', 0),
            'diamond': kwargs.get('diamond', 0),
        }
        return data

    def _pre_check_list(self, data):
        """
        检查数据
            1 组装检查列表
            2 检查数据(检查出错会跑出异常)
            3 返回检查完毕列表(检查通过)
        """
        check_list = []
        if data['gold'] or data['diamond']:
            check_list.append(self._club_resource_check(data['gold'], data['diamond']))

        for cb in check_list:
            cb.next()

        return check_list

    @staticmethod
    def _post_check(check_list):
        """
        资源扣除, 接在 _pre_check_list 后
        """
        for func in check_list:
            try:
                func.next()
            except StopIteration:
                pass

    def _club_resource_check(self, gold=0, diamond=0):
        """
        俱乐部资源检测扣除, 内部调用函数
            1 获取 玩家 俱乐部 实例
            2 检测资源是否足够( 不足, 返回对应提示 )
            3 yield
            4 扣除
        """
        from core.club import Club

        club = Club(self.server_id, self.char_id)

        if abs(gold) > club.gold and gold < 0:
            raise GameException(ConfigErrorMessage.get_error_id('GOLD_NOT_ENOUGH'))
        elif abs(diamond) > club.diamond and diamond < 0:
            raise GameException(ConfigErrorMessage.get_error_id('DIAMOND_NOT_ENOUGH'))

        yield

        club.update(gold=gold, diamond=diamond)
