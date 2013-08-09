#-*-coding:utf-8-*-

#
#http://pandavip.www.net.cn/check/check_ac1.cgi?domain=xingqiba.net&callback=&_=1376042461343
#("net|xingqiba.net|211|Domain exists");
#
#http://pandavip.www.net.cn/check/check_ac1.cgi?domain=xingqiba.cn&callback=&_=1376042461343
#("cn|xingqiba.cn|211|Domain name is not available");
#
#

from gevent import monkey;monkey.patch_all()
import gevent
from gevent.queue import Queue,Empty
import logging
import urllib2
import time
import sys
import traceback

logging.basicConfig(
    level   = logging.INFO,
    stream  = sys.stdout,
    datefmt = "%Y-%m-%d %H:%M:%S",
)

class Domain(object):

    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.post_url  = 'http://pandavip.www.net.cn/check/check_ac1.cgi?callback=&_=%s' % (time.time(), )
        #self.proxy()

    def proxy(self):
        proxy  = urllib2.ProxyHandler({'http':'127.0.0.1:8888'})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    def run(self):
        while True:
            try:
                task = self.msg_queue.get(timeout=3)
                if task:
                    url = "%s&domain=%s" % (self.post_url, task, )
                    result = urllib2.urlopen(url, timeout=60).read()
                    if result.count("Domain name is available") :
                        logging.info("domain=%s, result=%s", task, result)
                else:
                    break
            except Empty:
                break
            except:
                logging.error(traceback.format_exc())

def domain_check():
    msg_queue = Queue()
    spawn_list = []
    for x in range(100):
        m = Domain(msg_queue)
        spawn_list.append(gevent.spawn(m.run))

    domain_list = [
        'xingqiba.com',
        'xingqiba.cn',
        'xingqiba123.cn'
    ]
    for x in domain_list:
        msg_queue.put(x)

    gevent.joinall(spawn_list)

if __name__ == "__main__":
    domain_check()

