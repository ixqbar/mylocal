#-*-coding:utf-8-*-
from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
import gevent
import signal
import logging
import cppsclient
from gevent.socket import create_connection
from gevent.queue import Queue
import cppsutil
import inspect

class CppsTaskServer(object):
    """PhpServer"""

    def __init__(self, symbol, address, msg_queue, cli_conns):
        self.symbol    = symbol
        self.address   = address
        self.msg_queue = msg_queue
        self.cli_conns = cli_conns
        self.php_sock  = None

    def connect(self):
        if self.php_sock == None:
            try:
                self.php_sock  = create_connection(self.address)
            except:
                self.php_sock  = None
                logging.error("can't connect to php server `%s` ", self.address)

        return self.php_sock != None

    def close(self):
        if self.php_sock:
            self.php_sock.close()
            self.php_sock = None

    def process(self, req_msg):
        err_no, rep_msg = cppsutil.write_sock_buf(self.php_sock, req_msg)
        if 0 == err_no:
            logging.debug("start read from php server `%s`", self.php_sock)
            err_no, rep_msg = cppsutil.read_sock_buf(self.php_sock)
            if 0 == err_no:
                logging.info("write php response to client `%s`", rep_msg)
                self.cli_conns.php_to_cli(rep_msg)
            else:
                logging.error("read `%s` buf failure `%s`", self.php_sock, rep_msg)
        else:
            logging.error("write buf `%s` to php server failure `%s`", req_msg, rep_msg)

    def run(self):
        while self.connect():
            try:
                task = self.msg_queue.get()
                if task:
                    if self.connect():
                        logging.info("process php task `%s`", task)
                        self.process(task)
                    else:
                        self.msg_queue.put_nowait(task)
                        logging.error("can't connect php server,task `%s` put to queue", task)
            except:
                logging.error("dequeue error `%s`", inspect.stack())
            finally:
                gevent.sleep(0)

        logging.error("`%s` task server over", self.symbol)


class CppsRouteServer(StreamServer):
    """RouteServer extends StreamServer"""

    def __init__(self, listener, cli_timeout=60):
        StreamServer.__init__(self, listener)
        self.listener    = listener
        self.cli_timeout = cli_timeout
        self.php_cons    = dict()
        self.msg_queue   = Queue()
        self.cli_conns   = cppsclient.CppsClient(self.msg_queue)

    def handle(self, client_sock, address):
        """消息处理"""
        self.cli_conns.handle(client_sock, address)

    def connect_php_server(self, address):
        """中转服务"""
        for i in xrange(10):
            self.php_cons[i] = CppsTaskServer(i, address, self.msg_queue, self.cli_conns)
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


