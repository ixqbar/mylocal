#!/usr/bin/python
#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
from gevent.socket import create_connection
from gevent import core
import gevent

import cppsutil

class TClient(object):

    def __init__(self, address=("127.0.0.1", 2011)):
        self.cli_sock = create_connection(address)

        if self.cli_sock:
            self.accept_event = core.read_event(self.cli_sock.fileno(), self.do_read, persist=True)

    def get_msg(self):
        return '{"uid":1,"timstamp":"10"}'

    def do_read(self, event, evtype):
        if not event is self.accept_event:
            return

        response = cppsutil.read_sock_buf(self.cli_sock)
        print ("received:", response)

    def run(self):
        while self.cli_sock:
            msg = self.get_msg()
            result = cppsutil.write_sock_buf(self.cli_sock, msg)
            print result
            gevent.sleep(10)



if __name__ == '__main__':
    test = TClient()
    test.run()
