#-*-coding:utf-8-*-
import socket
import weakref
import errno
import json
import hashlib
import time
import inspect
import gevent
import logging
from gevent.queue import Queue
import cppsutil

FATALERROR  = (errno.EBADF, errno.EINVAL, errno.ENOTSOCK)
IGNOREERROR = (errno.EAGAIN, errno.EWOULDBLOCK)

class CppsClient(object):

    def __init__(self, msg_queue, max_conns=10000):
        """客户端连接消息处理"""
        self.msg_queue = msg_queue

    def close(self):
        pass

    def check_connect_timeout(self, timeout=60):
        pass

    def cli_request_msg_to_php(self, msg):
        self.msg_queue.put_nowait(msg)

    def php_response_msg_to_cli(self, msg):
        pass

    def handle(self):
        pass