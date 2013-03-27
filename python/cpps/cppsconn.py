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

    def get_sock_fd(self, client_sock):
        return str(client_sock.fileno())

    def dis_connect(self, client_sock, close_msg=None):
        """关闭"""
        logging.info("to disconnect %s %s" % (client_sock, close_msg))
        try:
            fd = self.get_sock_fd(client_sock)
            if fd in self.cli_conns:
                del self.cli_conns[fd]
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
        if not isinstance(msg ,str):
            result = (False, "error msg `{0}` type".format(msg))
            return result

        #like ['result', 'pull', 'clifd', 'uid', 'rid', 'ext_data']
        msg = msg.split("|", 5)

        logging.info("php response msg to cli `%s`", msg)
        if isinstance(msg, list) and 6 == len(msg) and "0" == msg[0]:
            if msg[1] == "pull":
                ##请求响应
                response_msg = {
                    'id'   : msg[4],
                    'data' : msg[5]
                }

                if msg[2] in self.cli_conns and self.cli_conns[msg[2]]['uid'] == msg[3]:
                    result = self.response_to_cli(self.cli_conns[msg[2]]['sock'], msg[3], response_msg)
                else:
                    result = (False, "client not exists for `{0}`".format(msg))

                if not result[0]:
                    logging.error("php write buf `%s` to cli `%s` failure", msg, self.cli_conns[msg[2]] if msg[2] in self.cli_conns else None)
                self.clients.add_no_response_msg(msg[3], msg[4], response_msg)
                logging.info("client `%s` no response msg `%s`", msg[3], self.clients.list_no_response_msg(msg[3]))
            else:
                #推响应
                response_msg = {
                    'id'   : 0,
                    'data' : msg[5]
                }
                target_uids = msg[3].split(",") if msg[3].count("|") else msg[3]
                for fd, conn in self.cli_conns.items():
                    if conn['uid'] is None:
                        continue
                    if isinstance(target_uids, list):
                        if conn['uid'] in target_uids:
                            self.response_to_cli(conn['sock'], conn['uid'], response_msg)
                    elif target_uids == "0" or conn['uid'] == target_uids:
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
        fd = self.get_sock_fd(client_sock)
        logging.info('new connection from %s:%s,fd=%s' % (address[0], address[1], fd,))
        self.cli_conns[fd] = {"sock" : client_sock, "time" : time.time(), "uid" : None}

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

        if fd in self.cli_conns:
            self.dis_connect(client_sock)

    def process_message(self, client_sock, msg):
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
                result = self.handlers[tmp_msg[0]](client_sock, tmp_msg[1], tmp_msg[2], tmp_msg[3])
            except:
                result = (False, traceback.format_exc())
                logging.error("an error occurred", exc_info=True)
            finally:
                lock.release()
        else:
            result = (False, "error message format `{0}`".format(msg))

        return result

    def login(self, client_sock, uid, rid, data):
        if isinstance(data, str):
            data = json.loads(data.decode('utf-8'), 'utf-8')

        if not isinstance(data, dict) or not "uid" in data or not "timestamp" in data:
            logging.error("error login message `%s` from `%s`", data, client_sock)
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"error login message format"}
            }
            self.ser_to_cli(client_sock, uid, json.dumps(response_message))
            return (False, "error login message format")

        hm = hashlib.md5();
        hm.update(self.secret_key + str(data["uid"]) + str(data["timestamp"]) + str(data["random"]))
        if uid != str(data['uid']) or data["sign"] != hm.hexdigest():
            logging.error("error login message `%s` from `%s`", data, client_sock)
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"error login message sign"}
            }
            self.ser_to_cli(client_sock, uid, json.dumps(response_message))
            return (False, "error login message sign")

        client_player_uid = cppsutil.to_str(uid)
        if client_player_uid in self.rel_mapping:
            self.dis_connect(self.rel_mapping[client_player_uid], "relogin")

        logging.info("login message `%s` from `%s`", data, client_sock)
        response_message = {
            "id"   : rid,
            "data" : {"err_id":""}
        }
        fd = self.get_sock_fd(client_sock)
        self.cli_conns[fd]['uid']       = client_player_uid
        self.rel_mapping[client_player_uid] = client_sock
        self.clients.login(data);
        self.ser_to_cli(client_sock, uid, json.dumps(response_message))

        return (True, "")

    def hello(self, client_sock, uid, rid, data):
        result = (True, "")
        fd = self.get_sock_fd(client_sock)
        if self.cli_conns[fd] is not None:
            self.cli_conns[fd]["time"] = time.time()
            response_message = {
                "id"   : rid,
                "data" : {"err_id":""}
            }
        else:
            response_message = {
                "id"   : rid,
                "data" : {"err_id":"not found target cli"}
            }

        self.ser_to_cli(client_sock, uid, json.dumps(response_message))

        return result

    def service(self, client_sock, uid, rid, data):
        result = (True, "")
        fd = self.get_sock_fd(client_sock)
        if self.clients.is_reconnect(uid):
            no_response_msg = self.clients.get_no_response_msg(uid, rid)
            if no_response_msg:
                result = self.ser_to_cli(client_sock, uid, json.dumps(no_response_msg))
                if not result[0]:
                    self.clients.add_no_response_msg(uid,rid,no_response_msg)
            else:
                self.cli_to_php({'cli':fd,'uid':uid,'rid':rid,'data':data})
        else:
            self.cli_to_php({'cli':fd,'uid':uid,'rid':rid,'data':data})

        return result
