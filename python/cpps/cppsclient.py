#-*-coding:utf-8-*-

import cppsutil

class CppsClient(object):

    def __init__(self):
        self.player = dict()

    def clear_no_response_msg(self, uid):
        uid = cppsutil.to_str(uid)
        if uid in self.player:
            self.player[uid]['no_response_msg'] = dict()

    def add_no_response_msg(self, uid, rid, msg):
        uid,rid = cppsutil.to_str(uid, rid)
        if uid in self.player:
            self.player[uid]['no_response_msg'][rid] = msg
            return True

        return False

    def get_no_response_msg(self, uid, rid):
        uid,rid = cppsutil.to_str(uid, rid)
        if uid in self.player and rid in self.player[uid]:
            return self.player[uid].pop(rid)
        else:
            return None

    def login(self, login_data):
        uid = cppsutil.to_str(login_data['uid'])
        if uid not in self.player:
            self.player[uid] = {
                'uid'             : uid,
                'reconnect'       : False,
                'no_response_msg' : dict()
            }

        if 'reconnect' not in login_data or 0 == int(login_data['reconnect']):
            self.player[uid]['reconnect'] = False
            self.clear_no_response_msg(uid)
        else:
            self.player[uid]['reconnect'] = True

    def is_reconnect(self, uid):
        uid = cppsutil.to_str(uid)

        return self.player[uid]['reconnect'] if uid in self.player else False
