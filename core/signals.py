# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signals
Date Created:   2015-04-30 15:20
Description:

"""

from django.dispatch import Signal

# TODO 清理

# 帐号登录
account_login_signal = Signal(providing_args=['account_id', 'ip', 'to_server_id'])
# 创建角色
char_created_signal = Signal(providing_args=['server_id', 'char_id', 'char_name'])
# 游戏开始
game_start_signal = Signal(providing_args=['server_id', 'char_id'])

# 进行了一场挑战赛
challenge_match_signal = Signal(providing_args=['server_id', 'char_id', 'challenge_id', 'win'])
# 好友切磋比赛
friend_match_signal = Signal(providing_args=['server_id', 'char_id', 'target_id', 'win'])
# 打了一次联赛
league_match_signal = Signal(providing_args=['server_id', 'char_id', 'target_id', 'win'])
# 打了一场天体赛
ladder_match_signal = Signal(providing_args=['server_id', 'char_id', 'target_id', 'win'])
# 报名参加了杯赛
join_cup_signal = Signal(providing_args=['server_id', 'char_id'])
# 聊天说了一句话
chat_signal = Signal(providing_args=['server_id', 'char_id'])
# 成为好友
friend_ok_signal = Signal(providing_args=['server_id', 'char_id', 'friend_id'])
# 升级了俱乐部
club_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'new_level'])
# 升级了员工
staff_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'new_level'])
# 获得新员工
staff_new_add_signal = Signal(providing_args=['server_id', 'char_id', 'oid', 'unique_id', 'force_load_staffs'])

# VIP
vip_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'new_level'])

# 员工强化培训
training_property_start_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
training_property_done_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
# 员工exp训练
training_exp_start_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
training_exp_done_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
training_exp_speedup_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
# staff broadcast
training_broadcast_start_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])

training_shop_start_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
training_sponsor_start_signal = Signal(providing_args=['server_id', 'char_id', 'sponsor_id'])

training_skill_start_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'skill_id'])
# 招募了员工
recruit_staff_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])

# 充值
purchase_done_signal = Signal(providing_args=['server_id', 'char_id', 'diamond'])

# 完成随机事件
random_event_done_signal = Signal(providing_args=['server_id', 'char_id', 'event_id'])

# 建筑升级 - 开始
building_level_up_start_signal = Signal(providing_args=['server_id', 'char_id', 'building_id'])
# 建筑升级 -结束
building_level_up_done_signal = Signal(providing_args=['server_id', 'char_id', 'building_id'])

# finish one daily task
daily_task_finish_signal = Signal(providing_args=['server_id', 'char_id', 'task_id'])

# 获得新道具
item_got_signal = Signal(providing_args=['server_id', 'char_id', 'items'])
# 获得技能训练书
training_skill_item_got_signal = Signal(providing_args=['server_id', 'char_id', 'items'])

# 坐车
in_car_signal = Signal(providing_args=['server_id', 'char_id'])
