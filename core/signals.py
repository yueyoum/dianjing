# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signals
Date Created:   2015-04-30 15:20
Description:

"""

from django.dispatch import Signal

# 帐号登录
account_login_signal = Signal(providing_args=['account_id', 'ip', 'to_server_id'])

# 游戏开始
game_start_signal = Signal(providing_args=['server_id', 'char_id'])

# 进行了一场挑战赛
challenge_match_signal = Signal(providing_args=['server_id', 'char_id', 'challenge_id', 'win'])
# 好友切磋比赛
friend_match_signal = Signal(providing_args=['server_id', 'char_id', 'target_id', 'win'])

# 竞技场比赛  参数里有 target_name，是因为可能对手是NPC
arena_match_signal = Signal(providing_args=['server_id', 'char_id', 'target_id', 'target_name', 'my_rank', 'target_rank', 'win', 'continue_win'])

# 聊天说了一句话
chat_signal = Signal(providing_args=['server_id', 'char_id'])
# 成为好友
friend_ok_signal = Signal(providing_args=['server_id', 'char_id', 'friend_id'])
# 升级了俱乐部
club_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'new_level'])

# 员工升级
staff_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'staff_oid', 'new_level'])
# 员工升阶
staff_step_up_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'staff_oid', 'new_step'])
# 员工升星
staff_star_up_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'staff_oid', 'new_star'])

# 获得新员工
staff_new_add_signal = Signal(providing_args=['server_id', 'char_id', 'oid', 'unique_id', 'force_load_staffs'])

# VIP
vip_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'new_level'])


# 招募了员工
recruit_staff_diamond_signal = Signal(providing_args=['server_id', 'char_id', 'times', 'staffs'])
recruit_staff_gold_signal = Signal(providing_args=['server_id', 'char_id', 'times', 'staffs'])

# 充值
purchase_done_signal = Signal(providing_args=['server_id', 'char_id', 'diamond'])

# 任务条件触发
task_condition_trig_signal = Signal(providing_args=['server_id', 'char_id', 'condition_name'])
