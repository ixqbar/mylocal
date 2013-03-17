#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
from gevent.socket import create_connection
import sys
sys.path.append("..")
import cppsutil
import logging

logging.basicConfig(
    level   = logging.DEBUG,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format  = "[%(asctime)s]%(levelname)8s-%(filename)15s-%(funcName)30s-%(lineno)5s:%(message)s"
)

php_sock  = create_connection(('127.0.0.1', 9090))
req_msg = {
    'cli' : 1,
    'msg' : 'hello world'
}
print cppsutil.write_sock_buf(php_sock, req_msg)

print cppsutil.read_sock_buf(php_sock)
