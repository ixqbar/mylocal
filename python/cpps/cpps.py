#!/usr/bin/python
#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
import os
import sys
import time
import optparse
import logging
import cppsserver
import inspect

logging.basicConfig(
    level    = logging.DEBUG,
    filename = os.path.join(os.getcwd(), "run.log"),
    datefmt  = "%Y-%m-%d %H:%M:%S",
    format   = "[%(asctime)s]%(levelname)8s-%(filename)15s-%(funcName)30s-%(lineno)5s:%(message)s"
)

parser = optparse.OptionParser(description="This is a chat server")
parser.add_option("--port",     dest="port",     action="store", type="int",    help="port")
parser.add_option("--timezone", dest="timezone", action="store", type="string", help="timezone")
parser.add_option("--php_host", dest="php_host", action="store", type="string", help="php_host")
parser.add_option("--php_port", dest="php_port", action="store", type="string", help="php_port")
parser.add_option("--timeout",  dest="timeout",  action="store", type="int",    help="set max seconds for a connection timeout default 60 seconds")
parser.set_defaults(port=8080,
                    timezone="UTC",
                    php_host="127.0.0.1",
                    php_port=9090,
                    timeout=60)
opt,args = parser.parse_args()

if __name__ == "__main__":
    try:
        os.environ["TZ"] = opt.timezone
        time.tzset()
        server = cppsserver.CppsServer(("0.0.0.0", opt.port), opt.timeout)
        server.connect_php_server((opt.php_host,opt.php_port))
        server.run()
    except:
        logging.error(inspect.trace())

    logging.info("chat server run stop")
    sys.exit(0)
