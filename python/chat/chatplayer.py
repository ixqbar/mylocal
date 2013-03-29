#-*-coding:utf-8-*-

import time

class ChatPlayer(object):

    def __init__(self):
        self.uid        = ""
        self.name       = ""
        self.first_name = ""
        self.last_name  = ""
        self.level      = 0
        self.gid        = 0

    def __str__(self):
        return '{"uid":"%s","first":"%s","last":"%s","level":"%s","gid":"%s"}' \
               % (self.uid, self.first_name, self.last_name,self.level, self.gid)

    def refresh_data(self, user_info = dict()):
        if 'uid' in user_info:
            self.uid = user_info['uid']
        if 'name' in user_info:
            self.name = user_info['name']
        if 'first' in user_info:
            self.first_name = user_info['first']
        if 'last' in user_info:
            self.last_name = user_info['last']
        if 'level' in user_info:
            self.level = user_info['level']
        if 'gid' in user_info:
            self.gid = user_info['gid']
