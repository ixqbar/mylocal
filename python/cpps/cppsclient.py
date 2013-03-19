#-*-coding:utf-8-*-
import socket
import weakref
import json
import hashlib
import time
import inspect
import gevent
import logging
from gevent.queue import Queue
import cppsutil

class CppsClient(object):

    def __init__(self, msg_queue):
        """客户端连接消息处理"""
        self.msg_queue = msg_queue
        self.cli_conns = dict()

    def close(self):
        pass

    def check_cli_timeout(self, timeout=60):
        pass

    def cli_to_php(self, msg):
        self.msg_queue.put_nowait(msg)

    def php_to_cli(self, msg):
        result = (1, "error php response to cli")
        if isinstance(msg ,str):
            msg = json.loads(msg.decode("utf-8"))

        logging.info("php response msg to cli `%s`", msg)
        if 0 == msg[0]:
            if self.cli_conns[msg[1]['cli']]:
                result = cppsutil.write_sock_buf(self.cli_conns[msg[1]['cli']]['sock'], json.dumps(msg[1]['msg']))
                logging.info("php response to %s msg `%s` result %s", self.cli_conns[msg[1]['cli']]['sock'], msg[1]['msg'], result)
            else:
                logging.error("client not exists for `%s`", msg)
        else:
            logging.error("php response error `%s`", msg[1])

        return result

    def handle(self, client_sock, address):
        client_sock_fd = client_sock.fileno()
        logging.info('new connection from %s:%s,fd=%s' % (address[0], address[1], client_sock_fd,))
        self.cli_conns[client_sock_fd] = {"sock" : client_sock, "time" : time.time(), "uid" : ""}

        self.cli_to_php({'cli' : client_sock_fd, "msg" : "hi,I'am a tester"})