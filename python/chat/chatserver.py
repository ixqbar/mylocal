#-*-coding:utf-8-*-
from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
import gevent
import signal
import errno
import logging
import chatmessage

NONBLOCKING = (errno.EAGAIN, errno.EWOULDBLOCK)

class ChatServer(StreamServer):
    """ChatServer extends StreamServer"""

    def __init__(self, listener, maxconns=1000, timeout=60):
        StreamServer.__init__(self, listener)
        self.listener    = listener
        self.logging     = logging
        self.timeout     = timeout
        self.chatmessage = chatmessage.ChatMessage(maxconns)

    def handle(self, client_socket, address):
        """ deal client connect """
        self.logging.info('new connection from %s:%s,fd=%s' % (address[0], address[1], client_socket.fileno()))
        self.chatmessage.process_read_message(client_socket)

    def run(self):
        self.logging.info("server starting run on %s:%s" % self.listener)
        gevent.signal(signal.SIGINT, self.close, signal.SIGINT)
        gevent.signal(signal.SIGTERM, self.close, signal.SIGTERM)
        self._spawn(self.chatmessage.check_connect_timeout, self.timeout)
        self.serve_forever()

    def close(self, signo):
        self.logging.info("server catch signal %d" % (signo,))
        self.chatmessage.close()
        self.kill()


