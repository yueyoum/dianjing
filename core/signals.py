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
# 创建角色
char_created_signal = Signal(providing_args=['char_id', 'char_name'])
# 游戏开始
game_start_signal = Signal(providing_args=['server_id', 'char_id'])
# 参赛员工设置完成
match_staffs_set_done_signal = Signal(providing_args=['server_id', 'char_id', 'match_staffs'])
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
# 招募了员工
recruit_staff_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id'])
# 升级了俱乐部
club_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'new_level'])
# 升级了员工
staff_level_up_signal = Signal(providing_args=['server_id', 'char_id', 'staff_id', 'new_level'])

# 充值
purchase_done_signal = Signal(providing_args=['server_id', 'char_id', 'diamond'])
# 训练获取奖励完毕
training_got_reward_signal = Signal(providing_args=['server_id', 'char_id', 'training_id'])
# 完成随机事件
random_event_done_signal = Signal(providing_args=['server_id', 'char_id', 'event_id'])
