#!/usr/bin/python
#-*-coding:utf-8-*-


'''
http://member.kaye.cn/Ajax_Member.aspx?Ajax=SMS
Mobile	13671527966
'''

from gevent import monkey;monkey.patch_all()
import gevent
from gevent.queue import Queue,Empty
import logging
import urllib2
import urllib
import time
import sys
import traceback

logging.basicConfig(
    level   = logging.INFO,
    stream  = sys.stdout,
    datefmt = "%Y-%m-%d %H:%M:%S",
)

class Mobile(object):

    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.post_url  = 'http://member.kaye.cn/Ajax_Member.aspx?Ajax=SMS'
        self.proxy()

    def proxy(self):
        proxy  = urllib2.ProxyHandler({'http':'127.0.0.1:8888'})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    def run(self):
        while True:
            try:
                task = self.msg_queue.get(timeout=3)
                logging.info("get mobile `%s` from queue", task)
                if task:
                    result = urllib2.urlopen(self.post_url, urllib.urlencode({'Mobile':task}), 60).read()
                    logging.info("time=%s, mobile=%s, result=%s", time.time(), task, result)
                else:
                    break
            except Empty:
                break
            except:
                logging.error(traceback.format_exc())

def send_mobile_sms():
    msg_queue = Queue()
    spawn_list = []
    for x in range(100):
        m = Mobile(msg_queue)
        spawn_list.append(gevent.spawn(m.run))

    start_mobile = ''
    for x in range(1, 100):
        start_mobile += 1
        msg_queue.put(start_mobile)

    gevent.joinall(spawn_list)

if __name__ == "__main__":
    try:
        send_mobile_sms()
    except:
        pass

