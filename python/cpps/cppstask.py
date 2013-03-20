#-*-coding:utf-8-*-

from gevent.socket import create_connection
import logging
import cppsutil
import gevent
import inspect

class CppsTask(object):
    """PhpServer"""

    def __init__(self, task_name, address, msg_queue, cli_conns):
        self.task_name = task_name
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
        result = cppsutil.write_sock_buf(self.php_sock, req_msg)
        if result[0]:
            logging.debug("start read from php server `%s`", self.php_sock)
            result = cppsutil.read_sock_buf(self.php_sock)
            if result[0]:
                logging.info("write php response to client `%s`", result)
                self.cli_conns.php_to_cli(result[1])
            else:
                logging.error("read `%s` buf failure `%s`", self.php_sock, result)
        else:
            logging.error("write buf `%s` to php server failure `%s`", result)

    def run(self):
        while True:
            try:
                task = self.msg_queue.get()
                if task:
                    if self.connect():
                        logging.info("process php task `%s`", task)
                        self.process(task)
                        gevent.sleep(0)
                    else:
                        self.msg_queue.put_nowait(task)
                        logging.error("can't connect php server task `%s` put to queue", task)
                        gevent.sleep(10)
                else:
                    logging.error("empty task item from queue")
            except:
                logging.error("task server error `%s`", inspect.stack())
