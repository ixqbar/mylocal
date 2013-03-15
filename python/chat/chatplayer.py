#-*-coding:utf-8-*-

import time

class ChatPlayer(object):

    def __init__(self):
        self.uid         = ""
        self.name        = ""
        self.first_name  = ""
        self.last_name   = ""
        self.level       = 0
        self.active_time = 0
        self.logined     = False

    def __str__(self):
        return '{"uid":"%s","first":"%s","last":"%s","level":"%s","time":"%s","logined":"%s"}' \
               % (self.uid, self.first_name, self.last_name,self.level, self.active_time, self.logined)

    def refresh_data(self, user_info = dict()):
        self.uid         = user_info.get("uid", "")
        self.name        = user_info.get("name", "")
        self.first_name  = user_info.get("first", "")
        self.last_name   = user_info.get("last", "")
        self.level       = user_info.get("level", 0)
        self.active_time = time.time()
        self.logined     = True
