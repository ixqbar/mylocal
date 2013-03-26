#-*-coding:utf-8-*-
import json
import hashlib
import time
import gevent
import logging
import traceback
import weakref
import cppsutil
import cppsclient
from gevent.coros import Semaphore

class CppsConn(object):

    def __init__(self, msg_queue):
        """客户端连接消息处理"""
        self.secret_key  = ""
        self.msg_queue   = msg_queue
        self.no_response = dict()
        self.cli_conns   = dict()
        self.lock        = dict()
        self.rel_mapping = weakref.WeakValueDictionary()
        self.clients     = cppsclient.CppsClient()
        self.handlers    = {
            "login"   : self.login,
            "hello"   : self.hello,
            "service" : self.service,
            }

    def get_lock(self, uid):
        uid = cppsutil.to_str(uid)
        if len(uid) > 0:
            if uid not in self.lock:
                self.lock[uid] = Semaphore()
        else:
            return Semaphore()

        return self.lock[uid]

    def dis_connect(self, client_sock, close_msg=None):
        """关闭"""
        logging.info("to disconnect %s %s" % (client_sock, close_msg))
        try:
            client_socket_fd = client_sock.fileno()
            if client_socket_fd in self.cli_conns:
                del self.cli_conns[client_socket_fd]
            client_sock.close()
        except:
            logging.error("an error occurred", exc_info=True)
            return (False, traceback.format_exc())

        return (True, "")

    def close(self):
        for fd, conn in self.cli_conns.items():
            conn["sock"].close()
            del self.cli_conns[fd]

    def check_cli_timeout(self, timeout=60):
        while True:
            if len(self.cli_conns):
                logging.info("check_connect_timeout start total connection %s" % (len(self.cli_conns),))
                check_time = time.time() - timeout
                for fd, conn in self.cli_conns.items():
                    if conn["time"] <= check_time:
                        self.dis_connect(conn["socket"], "check_connect_timeout")
                logging.info("check_connect_timeout end total connection %s" % (len(self.cli_conns),))
            gevent.sleep(30)

    def cli_to_php(self, msg):
        self.msg_queue.put_nowait(msg)


    def response_to_cli(self, cli_sock, uid, msg):
        result = (True, "")
        if isinstance(msg, dict):
            msg = json.dumps(msg)

        lock = self.get_lock(uid)
        lock.acquire()
        try:
            result = cppsutil.write_sock_buf(cli_sock, msg)
        except:
            result = (False, traceback.format_exc())
            logging.error("an error occurred", exc_info=True)
        finally:
            lock.release()

        return result

    def php_to_cli(self, msg):
        result = (True, "")
        if isinstance(msg ,str):
            msg = json.loads(msg.decode("utf-8"), "utf-8")

        logging.info("php response msg to cli `%s`", msg)
        if isinstance(msg, list) \
            and 2 == len(msg) \
            and 0 == msg[0] \
            and "action" in msg[1] \
            and "cli" in msg[1] \
            and "rid" in msg[1] \
            and "uid" in msg[1] \
            and "data" in msg[1]:

            if msg[1]['action'] == "pull":
                ##请求响应
                response_msg = {
                    'id'   : msg[1]['rid'],
                    'data' : msg[1]['data']
                }
                if msg[1]['cli'] in self.cli_conns and self.cli_conns[msg[1]['cli']]['uid'] == msg[1]['uid']:
                    result = self.response_to_cli(self.cli_conns[msg[1]['cli']]['sock'], msg[1]['uid'], response_msg)
                else:
                    result = (False, "client not exists for `{0}`".format(msg))

                if not result[0]:
                    logging.error("php write buf `%s` to cli `%s` failure", msg, self.cli_conns[msg[1]['cli']] if msg[1]['cli'] in self.cli_conns else None)
                self.clients.add_no_response_msg(msg[1]['uid'], msg[1]['rid'], response_msg)
                logging.info("client `%s` no response msg `%s`", msg[1]['uid'], self.clients.list_no_response_msg(msg[1]['uid']))
            else:
                #推响应
                response_msg = {
                    'id'   : 0,
                    'data' : msg[1]['data']
                }
                for fd, conn in self.cli_conns.items():
                    if conn['uid'] is None:
                        continue
                    if isinstance(msg[1]['uid'], str):
                        if msg[1]['uid'] == conn['uid']:
                            self.response_to_cli(conn['sock'], conn['uid'], response_msg)
                    elif isinstance(msg[1]['uid'], list):
                        if conn['uid'] in msg[1]['uid']:
                            self.response_to_cli(conn['sock'], conn['uid'], response_msg)
                    else:
                        self.response_to_cli(conn['sock'], conn['uid'], response_msg)
        else:
            logging.error("php response error `%s`", msg)
            result = (False,"error msg format `{0}`".format(msg))

        return result

    def ser_to_cli(self, client_sock, uid, message):
        """写数据"""
        result = (True, "")
        logging.info("write response message `%s` to %s" % (message, client_sock))
        try:
            result = cppsutil.write_sock_buf(client_sock, message)
            if not result[0]:
                logging.error("write response message to `%s` failure `%s`", client_sock, result)
                self.dis_connect(client_sock)
        except:
            result = (False, traceback.format_exc())
            logging.error("an error occurred", exc_info=True)
            self.dis_connect(client_sock)

        return result

    def handle(self, client_sock, address):
        client_sock_fd = client_sock.fileno()
        logging.info('new connection from %s:%s,fd=%s' % (address[0], address[1], client_sock_fd,))
        self.cli_conns[client_sock_fd] = {"sock" : client_sock, "time" : time.time(), "uid" : None}

        while True:
            try:
                result = cppsutil.read_sock_buf(client_sock)
                if not result[0]:
                    logging.error(result[1])
                    break;
                result = self.process_message(client_sock, result[1])
                if not result[0]:
                    logging.error("handle cli msg failure `%s`", result[1])
                    break;
            except:
                logging.error("an error occurred", exc_info=True)
                break;

        if client_sock_fd in self.cli_conns:
            self.dis_connect(client_sock)

    def process_message(self, cli_sock, msg):
        """消息处理"""
        result = (True, "")

        logging.info("receive message `%s`" % (msg,))
        tmp_msg = msg.split("|", 3)
        if 4 == len(tmp_msg) \
            and tmp_msg[0] in self.handlers \
            and len(tmp_msg[1]) > 0:
            lock = self.get_lock(tmp_msg[1])
            lock.acquire()
            try:
                result = self.handlers[tmp_msg[0]](cli_sock, tmp_msg[1], tmp_msg[2], tmp_msg[3])
            except:
                result = (False, traceback.format_exc())
                logging.error("an error occurred", exc_info=True)
            finally:
                lock.release()
        else:
            result = (False, "error message format `{0}`".format(msg))

        return result

    def login(self, cli_sock, uid, rid, data):
        if isinstance(data, str):
            data = json.loads(data.decode('utf-8'), 'utf-8')

        if not isinstance(data, dict) or not "uid" in data or not "timestamp" in data:
            logging.error("error login message `%s` from `%s`", data, cli_sock)
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"error login message format"}
            }
            self.ser_to_cli(cli_sock, uid, json.dumps(response_message))
            return (False, "error login message format")

        hm = hashlib.md5();
        hm.update(self.secret_key + str(data["uid"]) + str(data["timestamp"]) + str(data["random"]))
        if uid != str(data['uid']) or data["sign"] != hm.hexdigest():
            logging.error("error login message `%s` from `%s`", data, cli_sock)
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"error login message sign"}
            }
            self.ser_to_cli(cli_sock, uid, json.dumps(response_message))
            return (False, "error login message sign")

        client_player_uid = cppsutil.to_str(uid)
        if client_player_uid in self.rel_mapping:
            self.dis_connect(self.rel_mapping[client_player_uid], "relogin")

        logging.info("login message `%s` from `%s`", data, cli_sock)
        response_message = {
            "id"   : rid,
            "data" : {"err_id":""}
        }
        cli_fd = cli_sock.fileno()
        self.cli_conns[cli_fd]['uid']       = client_player_uid
        self.rel_mapping[client_player_uid] = cli_sock
        self.clients.login(data);
        self.ser_to_cli(cli_sock, uid, json.dumps(response_message))

        return (True, "")

    def hello(self, cli_sock, uid, rid, data):
        result = (True, "")

        if self.cli_conns[cli_sock.fileno()] is not None:
            self.cli_conns[cli_sock.fileno()]["time"] = time.time()
            response_message = {
                "id"   : rid,
                "data" : {"err_id":""}
            }
        else:
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"not found target cli"}
            }

        self.ser_to_cli(cli_sock, uid, json.dumps(response_message))

        return result

    def service(self, cli_sock, uid, rid, data):
        result = (True, "")
        cli_fd = cli_sock.fileno()
        if self.clients.is_reconnect(uid):
            no_response_msg = self.clients.get_no_response_msg(uid, rid)
            if no_response_msg:
                result = self.ser_to_cli(cli_sock, uid, json.dumps(no_response_msg))
                if not result[0]:
                    self.clients.add_no_response_msg(uid,rid,no_response_msg)
            else:
                self.cli_to_php({'cli':cli_fd,'uid':uid,'rid':rid,'data':data})
        else:
            self.cli_to_php({'cli':cli_fd,'uid':uid,'rid':rid,'data':data})

        return result
