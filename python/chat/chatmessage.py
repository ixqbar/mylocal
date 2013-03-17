#-*-coding:utf-8-*-
import socket
import weakref
import errno
import json
import hashlib
import time
import chatplayer
import inspect
import gevent
import logging

FATALERROR  = (errno.EBADF, errno.EINVAL, errno.ENOTSOCK)
IGNOREERROR = (errno.EAGAIN, errno.EWOULDBLOCK)

class ChatMessage(object):

    def __init__(self, maxconns=10000):
        """客户端连接消息处理"""
        self.login_key = "brEakgAMe"
        self.logging   = logging
        self.maxconns  = maxconns
        self.conns     = dict()
        self.player    = dict()                         #uid=>ChatPlayer()
        self.mapping   = weakref.WeakValueDictionary()  #uid=>socket.fileno()
        self.handlers  = {
            "login" : self.login,
            "hello" : self.hello,
            "chat"  : self.chat,
        }
        self.history   = list()

    def get_format_time(self):
        return time.strftime("%Y/%m/%d %H:%M:%S")

    def check_connect_timeout(self, timeout=60):
        while True:
            if len(self.conns):
                self.logging.info("check_connect_timeout start total connection %s" % (len(self.conns),))
                check_time = time.time() - timeout
                for fd, conn in self.conns.items():
                    if conn["time"] <= check_time:
                        self.dis_connect(conn["socket"], "check_connect_timeout")
                self.logging.info("check_connect_timeout end total connection %s" % (len(self.conns),))
            gevent.sleep(10)

    def get_history(self):
        return self.history

    def add_history(self, message):
        self.history.append(message)
        if len(self.history) > 100:
            self.history = self.history[-50:]

    def close(self):
        """关闭"""
        for fd, conn in self.conns.items():
            conn["socket"].close()
            del self.conns[fd]

    def dis_connect(self, client_socket, close_msg=None):
        """关闭"""
        self.logging.info("to disconnect %s %s" % (client_socket, close_msg))
        try:
            client_socket_fd = client_socket.fileno()
            if client_socket_fd in self.conns:
                del self.conns[client_socket_fd]
        except:
            self.logging.error("an error occurred disconnect %s, %s" % (client_socket, inspect.stack(),))
        finally:
            client_socket.close()

    def process_write_message(self, client_socket, message, action="rep"):
        """写数据"""
        response_message = str(len(message) + len(action) + 1).zfill(6) + action + " " + message + "|>"
        self.logging.info("write response message `%s` to %s" % (response_message, client_socket))

        response_message_len = len(response_message)
        start_send_position  = 0
        try:
            while True:
                try:
                    start_send_position += client_socket.send(response_message[start_send_position:])
                except socket.error as err:
                    if err.args[0] not in IGNOREERROR:
                        self.logging.error("error write response message `%s` to %s" % (response_message, client_socket))
                        self.dis_connect(client_socket)
                        break;

                self.logging.debug("write response message `%s` to %s len %s, total len %s" % (response_message, client_socket, start_send_position, response_message_len))
                if start_send_position == response_message_len:
                    break;
        except:
            self.logging.error("an error occurred %s" % (inspect.stack(),))
            self.dis_connect(client_socket)

    def process_read_message(self, client_socket):
        """读数据"""
        self.logging.info("client connected at %s" % (client_socket))
        client_socket_fd = client_socket.fileno()
        login_client_fd  = client_socket.fileno()
        self.conns[login_client_fd] = {"socket" : client_socket, "time" : time.time(), "uid" : ""}

        head_len         = 6
        to_read_len      = head_len
        read_head        = True
        read_body        = False
        body_len         = 0
        no_error         = True
        head_buff        = ""   #@TODO
        body_buff        = ""   #@TODO
        close_client     = True

        try:
            while no_error:
                while read_head:
                    close_client = True
                    try:
                        self.logging.debug("read head message len %d" % (to_read_len,))
                        tmp_head_buff = client_socket.recv(to_read_len)
                    except socket.error as err:
                        if err.args[0] not in IGNOREERROR:
                            no_error     = False
                            close_client = err.args[0] not in FATALERROR
                            self.logging.error("read socket error `%s`, %s" % (err, client_socket,))
                            break

                    self.logging.debug("read tmp head message %s,head_buff=%s" % (tmp_head_buff, head_buff))
                    if not tmp_head_buff or not tmp_head_buff.isdigit():
                        no_error = False
                        self.logging.error("can't read tmp head message %s %s" % (tmp_head_buff, client_socket,))
                        break;

                    head_buff += tmp_head_buff
                    if len(tmp_head_buff) == to_read_len:
                        read_head   = False
                        read_body   = True
                        to_read_len = int(head_buff) + 2
                        self.logging.debug("read head over,body len %d, head_buff=%s" % (to_read_len,head_buff))
                    else:
                        to_read_len -= len(head_buff)
                        self.logging.debug("read head loop,head len %d" % (to_read_len,))

                if not no_error:
                    break;

                while read_body:
                    close_client = True
                    try:
                        self.logging.debug("read body message len %d" % (to_read_len,))
                        tmp_body_buff = client_socket.recv(to_read_len)
                    except socket.error as err:
                        if err.args[0] not in IGNOREERROR:
                            no_error     = False
                            close_client = err.args[0] not in FATALERROR
                            self.logging.error("read socket error `%s`, %s" % (err, client_socket,))
                            break

                    self.logging.debug("read tmp body message `%s`, len=%s" % (tmp_body_buff, to_read_len))
                    if 0 == len(tmp_body_buff):
                        no_error = False
                        self.logging.error("can't read tmp body message %s" % (client_socket,))
                        break;

                    body_buff += tmp_body_buff
                    if len(tmp_body_buff) == to_read_len:
                        result      = "ok"
                        read_head   = True
                        read_body   = False
                        to_read_len = head_len
                        head_buff   = ""
                        self.logging.debug("read body over,body message `%s`" % (body_buff,))
                        if body_buff[-2:] == "|>":
                            try:
                                (result, close_client) = self.process_message(client_socket, body_buff[:-2])
                            except:
                                self.logging.error("an exception error occurred `%s`, %s" % (body_buff[:-2], inspect.stack()))
                            body_buff = ""
                            no_error  = result == "ok"
                        else:
                            self.logging.error("invalid body message end flags `%s`" % (body_buff,))
                            no_error = False
                    else:
                        to_read_len -= len(body_buff)
                        self.logging.debug("read body loop,body len %d" % (to_read_len,))
        except:
            self.logging.error("exception occurred %s" % (inspect.stack()))
            response_message = {
                "type"   : "unknown",
                "result" : "err",
                "err_id" : 0,
                "msg"    : "exception occurred"
            }
            self.process_write_message(client_socket, json.dumps(response_message))
            self.dis_connect(client_socket)

        if not no_error and close_client:
            self.logging.info("read error occurred to disconnect %s" % (client_socket,))
            self.dis_connect(client_socket)
        else:
            if client_socket_fd in self.conns:
                del self.conns[client_socket_fd]
            self.logging.info("read error occurred to del socket fd %s" % (client_socket_fd,))

    def process_message(self, client_socket, message):
        """todo"""
        self.logging.info("receive message `%s`" % (message,))
        chat_message = message.split(" ", 1)
        chat_action  = chat_message[0].lower()
        if  chat_action in self.handlers:
            return self.handlers[chat_action](client_socket, chat_message[1])

        return ("error message action", True)

    def login(self, client_socket, message):
        """
            login {"uid":"xxx", "first":"xxxx", "last":"xxxx", "timestamp":xxx, "random":"xx", "sign":"yyyyyyyyyyyy"}
            sign = MD5.hash(密钥+uid + timestamp + random)
        """

        if len(self.conns) > self.maxconns:
            self.logging.error("max conn, disconnect %s" % (client_socket,))
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 0,
                "msg"    : "max connected"
            }
            self.process_write_message(client_socket, json.dumps(response_message))
            self.dis_connect(client_socket)
            return ("max connected", False)

        self.logging.info("handle login message `%s`, %s" % (message, client_socket))
        login_message = json.loads(message.decode('utf-8'), "utf-8")
        if "uid" not in login_message \
            or "first" not in login_message \
            or "last" not in login_message \
            or "timestamp" not in login_message \
            or "random" not in login_message \
            or "sign" not in login_message:
            self.logging.error("receive error login message attribute `%s`" % (message,))
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 0,
                "msg"    : "error login message attribute"
            }
            self.process_write_message(client_socket, json.dumps(response_message))
            self.dis_connect(client_socket)
            return ("error login message attribute", False)

        hm = hashlib.md5();
        hm.update(self.login_key + str(login_message["uid"]) + str(login_message["timestamp"]) + str(login_message["random"]))
        if login_message["sign"] != hm.hexdigest():
            self.logging.error("receive error sign login message `%s`" % (message,))
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 1,
                "msg"    : "error login message sign"
            }
            self.process_write_message(client_socket, json.dumps(response_message))
            self.dis_connect(client_socket)
            return ("error login message sign", False)

        login_client_uid = str(login_message["uid"])
        login_client_fd  = client_socket.fileno()
        self.mapping[login_client_uid] = client_socket
        self.conns[login_client_fd]    = {"socket" : client_socket, "time" : time.time(), "uid" : login_client_uid}
        if self.player.get(login_client_uid) is None:
            self.player[login_client_uid]  = chatplayer.ChatPlayer()
        self.player[login_client_uid].refresh_data(login_message)

        response_message = {
            "type"    : "login",
            "result"  : "ok",
            "history" : self.get_history()
        }
        self.process_write_message(client_socket, json.dumps(response_message))

        return ("ok", False)

    def hello(self, client_socket, message):
        """
            hello timestamp
        """
        self.logging.info("handle hello message `%s`" % (message,))
        if self.conns[client_socket.fileno()] is not None:
            self.conns[client_socket.fileno()]["time"] = time.time()
        else:
            self.logging.error("handle hello message `%s` error none %s" % (message, client_socket,))

        return ("ok", False)

    def chat(self, client_socket, message):
        """
            私信请求
            chat {"type":0, "target":"1000018","msg":"xxxxxxxxxxxx" }
            #小喇叭
            chat {"type":1, "msg":"xxxxxxxxxxxx" }
            #大喇叭
            chat {"type":2, "msg":"xxxxxxxxxxxx" }
        """

        self.logging.info("handle chat message `%s`" % (message,))
        chat_message = json.loads(message.decode('utf-8'))
        if int(chat_message["type"]) not in (0, 1, 2):
            self.logging.error("receive error type chat message `%s`" % (message,))
            error_response_message = json.dumps({
                "type"     : "chat",
                "result"   : "err",
                "msg_type" : chat_message["type"],
                "msg"      : "error type"
            })
            self.process_write_message(client_socket, error_response_message)
            return ("error chat message type", False)

        sender_client_fileno = client_socket.fileno()
        sender_client_uid    = self.conns[sender_client_fileno].get("uid", None) if self.conns[sender_client_fileno] else None
        sender_client_player = self.player.get(sender_client_uid, None) if sender_client_uid else None
        if sender_client_uid is None or sender_client_player is None:
            self.logging.error("receive error uid chat message `%s`, %s, %d" % (message, client_socket, len(self.conns)))
            error_response_message = json.dumps({
                "type"     : "chat",
                "result"   : "err",
                "msg_type" : chat_message["type"],
                "msg"      : "error to fix uid"
            })
            self.process_write_message(client_socket, error_response_message)
            return ("error chat message uid", False)

        if int(chat_message["type"]) in (1, 2):
            response_message = json.dumps({
                "type"     : "chat",
                "result"   : "ok",
                "msg_type" : chat_message["type"],
            })
            self.process_write_message(client_socket, response_message)

            response_message = {
                "type"     : chat_message["type"],
                "sender"   : sender_client_uid,
                "name"     : sender_client_player.name,
                "level"    : sender_client_player.level,
                "first"    : sender_client_player.first_name,
                "last"     : sender_client_player.last_name,
                "msg"      : chat_message["msg"],
                "add_time" : self.get_format_time()
            }
            response = json.dumps(response_message)
            self.logging.info("response chat message to all `%s`" % (response,))
            for conn in self.conns.values():
                self.logging.info("response chat message loop `%s`" % (conn,))
                self.process_write_message(conn["socket"], response, "get_chat")
            self.add_history(response_message)
        else:
            target_client_uid = str(chat_message["target"]) if chat_message["target"] else None
            if  target_client_uid is not None and target_client_uid in self.player and target_client_uid in self.mapping:
                response_message = json.dumps({
                    "type"     : "chat",
                    "result"   : "ok",
                    "msg_type" : chat_message["type"],
                })
                self.process_write_message(client_socket, response_message)
                response_message = {
                    "type"     : chat_message["type"],
                    "sender"   : sender_client_uid,
                    "name"     : sender_client_player.name,
                    "level"    : sender_client_player.level,
                    "first"    : sender_client_player.first_name,
                    "last"     : sender_client_player.last_name,
                    "msg"      : chat_message["msg"],
                    "add_time" : self.get_format_time()
                }
                response = json.dumps(response_message)
                self.logging.info("response chat message to one `%s`, target %s" % (response, self.mapping[target_client_uid],))
                self.process_write_message(self.mapping[target_client_uid], response, "get_chat")
                self.add_history(response_message)
            else:
                response_message = {
                    "type"     : "chat",
                    "result"   : "err",
                    "msg_type" : chat_message["type"],
                    "msg"      : "error to fix target"
                }
                self.process_write_message(client_socket, json.dumps(response_message))

        return ("ok", False)