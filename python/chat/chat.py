#!/usr/bin/python
#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
import os
import time
import optparse
import logging
import traceback
import chatserver

logging.basicConfig(
    level   = logging.INFO,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format  = "[%(asctime)s]%(levelname)8s-%(filename)15s-%(funcName)30s-%(lineno)5s:%(message)s"
)

parser = optparse.OptionParser(description="This is a chat server")
parser.add_option("--port",     dest="port",     action="store", type="int",    help="port")
parser.add_option("--timezone", dest="timezone", action="store", type="string", help="timezone")
parser.add_option("--maxconns", dest="maxconns", action="store", type="int",    help="accept max connection default 10000")
parser.add_option("--timeout",  dest="timeout",  action="store", type="int",    help="set max seconds for a connection timeout default 60 seconds")
parser.set_defaults(port=8080, timezone="UTC", maxconns=10000, timeout=60)
opt,args = parser.parse_args()

if __name__ == "__main__":
    try:
        os.environ["TZ"] = opt.timezone
        time.tzset()
        server = chatserver.ChatServer(("0.0.0.0", opt.port), opt.maxconns, opt.timeout)
        server.run()
    except:
        logging.error(traceback.format_exc())

    logging.info("chat server run stop")
    exit(0)
