#-*-coding:utf-8-*-
from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
import gevent
import signal
import logging
import chatmessage

class ChatServer(StreamServer):
    """ChatServer extends StreamServer"""

    def __init__(self, listener, timeout=60):
        StreamServer.__init__(self, listener)
        self.listener    = listener
        self.timeout     = timeout
        self.chatmessage = chatmessage.ChatMessage()

    def handle(self, client_socket, address):
        self.chatmessage.handle(client_socket, address)

    def run(self):
        logging.info("server starting run on %s:%s" % self.listener)
        gevent.signal(signal.SIGINT, self.close, signal.SIGINT)
        gevent.signal(signal.SIGTERM, self.close, signal.SIGTERM)
        self._spawn(self.chatmessage.check_connect_timeout, self.timeout)
        self.serve_forever()

    def close(self, signo):
        logging.info("server catch signal %d" % (signo,))
        self.chatmessage.close()
        self.kill()


