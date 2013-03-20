#!/usr/bin/python
#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
import sys
import os
import time
import logging
import inspect
import json
import random
import hashlib
import gevent

from gevent.socket import create_connection

sys.path.append("..")
import cppsutil


class TClient(object):

    def __init__(self,uid=1,address=("127.0.0.1", 8080)):
        self.secret_key = ""
        self.uid        = uid
        self.rid        = 1
        self.cli_sock   = create_connection(address)

    def get_login_msg(self):
        timestamp = time.time()
        trand     = random.random()
        hm = hashlib.md5();
        hm.update(self.secret_key + str(self.uid) + str(timestamp) + str(trand))
        sign = hm.hexdigest()

        return 'login|' + str(self.uid) + "|" + str(self.rid) + "|" + json.dumps({'uid':self.uid, 'timestamp':timestamp,'reconnect':0,'random':trand,'sign':sign})

    def get_msg(self):

        if self.rid % 3 == 0:
            msg = {
                'id'      : self.rid,
                'uid'     : self.uid,
                'service' : ['player.hello']
            }
            return 'service|' + str(self.uid) + "|" + str(self.rid) + "|" + json.dumps(msg)
        else:
            msg = {
                'timestamp' : time.time()
            }
            return 'hello|' + str(self.uid) + "|" + str(self.rid) + "|" + json.dumps(msg)

    def run(self):
        #login
        logined = False
        while True:
            if not logined:
                msg = self.get_login_msg()
                logined = True
            else:
                msg = self.get_msg()
            print msg
            start_time = time.time()
            cppsutil.write_sock_buf(self.cli_sock, msg);
            response = cppsutil.read_sock_buf(self.cli_sock);
            print time.time() - start_time
            print response
            self.rid = self.rid + 1
            gevent.sleep(1)


if __name__ == '__main__':
    try:
        test = TClient()
        test.run()
    except:
        print(sys.exc_info())