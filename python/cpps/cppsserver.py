#-*-coding:utf-8-*-
from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
import gevent
import signal
import logging
import cppsconn
import cppstask
from gevent.queue import Queue

class CppsServer(StreamServer):
    """RouteServer extends StreamServer"""

    def __init__(self, listener, cli_timeout=60):
        StreamServer.__init__(self, listener)
        self.listener    = listener
        self.cli_timeout = cli_timeout
        self.php_cons    = dict()
        self.msg_queue   = Queue()
        self.cli_conns   = cppsconn.CppsConn(self.msg_queue)

    def handle(self, client_sock, address):
        """消息处理"""
        self.cli_conns.handle(client_sock, address)

    def connect_php_server(self, address):
        """中转服务"""
        for i in xrange(10):
            self.php_cons[i] = cppstask.CppsTask(i, address, self.msg_queue, self.cli_conns)
            gevent.spawn(self.php_cons[i].run)

    def run(self):
        """路由服务"""
        logging.info("server starting run on `%s:%s`" % self.listener)
        gevent.signal(signal.SIGINT, self.close, signal.SIGINT)
        gevent.signal(signal.SIGTERM, self.close, signal.SIGTERM)
        gevent.spawn(self.cli_conns.check_cli_timeout, self.cli_timeout)
        self.serve_forever()

    def close(self, signo):
        logging.info("server catch signal `%d`" % (signo,))
        for php_cons in self.php_cons.values():
            php_cons.close()
        self.cli_conns.close()
        self.kill()


