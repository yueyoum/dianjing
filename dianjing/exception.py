# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       exception
Date Created:   2015-04-22 15:34
Description:

"""

class GameException(Exception):
    def __init__(self, error_id, error_msg=""):
        self.error_id = error_id
        self.error_msg = error_msg

        Exception.__init__(self)
