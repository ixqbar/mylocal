#-*-coding:utf-8-*-
import weakref
import json
import hashlib
import time
import chatplayer
import gevent
import logging
import chatutil

class ChatMessage(object):

    def __init__(self, max_conns=10000):
        """客户端连接消息处理"""
        self.login_key = ""
        self.max_conns = max_conns
        self.conns     = dict()
        self.player    = dict()                         #uid=>ChatPlayer()
        self.mapping   = weakref.WeakValueDictionary()  #uid=>socket.fileno()
        self.handlers  = {
            "login"  : self.login,
            "update" : self.update,
            "hello"  : self.hello,
            "chat"   : self.chat,
            "notice" : self.notice
        }
        self.channel_history = {"public":[],"guild":{}}
        self.whisper_history = dict()

    def check_connect_timeout(self, timeout=60):
        while True:
            if len(self.conns):
                logging.info("check_connect_timeout start total connection %s", len(self.conns))
                check_time = time.time() - timeout
                for fd, conn in self.conns.items():
                    if conn["time"] <= check_time and 0 == conn['uid'].count("system"):
                        self.dis_connect(conn["socket"], "check_connect_timeout")
                logging.info("check_connect_timeout end total connection %s", len(self.conns))
            gevent.sleep(30)

    def get_all_history(self, target=0, guild_id=0):
        history = list()
        for message in self.get_public_history():
            history.append(message)

        if guild_id:
            for message in self.get_guild_history(guild_id):
                history.append(message)

        for message in self.get_whisper_history(target):
            history.append(message)

        return history

    def get_public_history(self):
        return self.channel_history['public']

    def get_guild_history(self, guild_id):
        return self.channel_history['guild'][guild_id] if guild_id and guild_id in self.channel_history['guild'] else []

    def get_whisper_history(self, target):
        return self.whisper_history[target] if target in self.whisper_history else []

    def add_history(self, message, target=0, guild_id=0):
        """
            message 消息
            target  接受者 0为大众
            guild_id 公会消息
        """
        if isinstance(target, int) and 0 == target:
            #公共聊天，包括公会
            if 0 == guild_id:
                #公共聊天
                self.channel_history['public'].append(message)
                if len(self.channel_history['public']) > 100:
                    self.channel_history['public'] = self.channel_history['public'][-50:]
            else:
                #公会聊天
                if guild_id not in self.channel_history['guild']:
                    self.channel_history['guild'][guild_id] = list()

                self.channel_history['guild'][guild_id].append(message)
                if len(self.channel_history['guild'][guild_id]) > 100:
                    self.channel_history['guild'][guild_id] = self.channel_history['guild'][guild_id][-50:]
        else:
            #私聊
            if target not in self.whisper_history:
                self.whisper_history[target] = list()

            self.whisper_history[target].append(message)
            if len(self.whisper_history[target]) > 100:
                self.whisper_history[target] = self.whisper_history[target][-50:]

    def close(self):
        """关闭"""
        for fd, conn in self.conns.items():
            conn["socket"].close()
            del self.conns[fd]

    def dis_connect(self, client_socket, close_msg=None):
        """关闭"""
        logging.info("to disconnect %s %s", client_socket, close_msg)
        try:
            client_socket_fd = client_socket.fileno()
            if client_socket_fd in self.conns:
                del self.conns[client_socket_fd]
            client_socket.close()
        except:
            return False

        return True

    def process_write_message(self, client_socket, message):
        """写数据"""
        logging.info("write response message `%s` to %s",  message, client_socket)
        try:
            err_no,err_msg = chatutil.write_sock_buf(client_socket, message)
            if err_no:
                logging.error("write response message to `%s` failure `%s`", client_socket, err_msg)
                self.dis_connect(client_socket)
        except:
            logging.error("an error occurred:", exc_info=True)
            self.dis_connect(client_socket)

    def handle(self, client_socket, address):
        """读数据"""
        logging.info("client `%s` connected `%s`", client_socket, address)
        client_socket_fd = client_socket.fileno()
        self.conns[client_socket_fd] = {"socket" : client_socket, "time" : time.time(), "uid" : "", "gid" : 0}

        while True:
            try:
                err_no,cli_msg = chatutil.read_sock_buf(client_socket)
                if err_no:
                    logging.error(cli_msg)
                    break;
                err_msg,to_close = self.process_message(client_socket, cli_msg)
                if to_close:
                    logging.error("handle cli msg failure `%s`", err_msg)
                    break;
            except:
                logging.error("an error occurred:", exc_info=True)
                break;

        if client_socket_fd in self.conns:
            self.dis_connect(client_socket)

    def process_message(self, client_socket, message):
        """todo"""
        logging.info("receive message `%s`", message)
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
        if len(self.conns) > self.max_conns:
            logging.error("max conn, disconnect %s", client_socket)
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 0,
                "msg"    : "max connected"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
            return ("max connected", True)

        logging.info("handle login message `%s`, %s", message, client_socket)
        login_message = json.loads(message.decode('utf-8'), "utf-8")
        if "uid" not in login_message \
            or "first" not in login_message \
            or "last" not in login_message \
            or "timestamp" not in login_message \
            or "random" not in login_message \
            or "sign" not in login_message:
            logging.error("receive error login message attribute `%s`", message)
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 0,
                "msg"    : "error login message attribute"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
            return ("error login message attribute", True)

        hm = hashlib.md5();
        hm.update(self.login_key + str(login_message["uid"]) + str(login_message["timestamp"]) + str(login_message["random"]))
        if login_message["sign"].upper() != hm.hexdigest().upper():
            logging.error("receive error sign login message `%s`", message)
            response_message = {
                "type"   : "login",
                "result" : "err",
                "err_id" : 1,
                "msg"    : "error login message sign"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
            return ("error login message sign", True)

        login_client_uid = str(login_message["uid"])
        login_client_gid = int(login_message['gid']) if 'gid' in login_message else 0
        login_client_fd  = client_socket.fileno()
        if login_client_uid in self.mapping:
            self.dis_connect(self.mapping[login_client_uid], "relogin")

        self.mapping[login_client_uid] = client_socket
        self.conns[login_client_fd]    = {
            "socket" : client_socket,
            "time"   : time.time(),
            "uid"    : login_client_uid,
            "gid"    : login_client_gid
        }
        if self.player.get(login_client_uid) is None:
            self.player[login_client_uid] = chatplayer.ChatPlayer()
        self.player[login_client_uid].refresh_data(login_message)

        response_message = {
            "type"    : "login",
            "result"  : "ok"
        }
        self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

        #聊天记录
        if 0 == login_client_uid.count('system'):
            all_history = self.get_all_history(login_client_uid,login_client_gid)
            if len(all_history):
                self.process_write_message(client_socket, 'get_chat ' + json.dumps(all_history))

        return ("ok", False)

    def update(self, client_socket, message):
        """
            update {"uid":x, "gid":x, "name":x, "","first":"","last":"","level":x}
        """
        logging.info("handle update message `%s`", message)
        update_message = json.loads(message.decode('utf-8'))
        if isinstance(update_message, dict) and "uid" in update_message:
            target_client_uid = str(update_message["uid"]) if update_message["uid"] else None
            if  target_client_uid is not None and target_client_uid in self.player and target_client_uid in self.mapping:
                ##
                if self.player.get(target_client_uid) is not None:
                    self.player[target_client_uid].refresh_data(update_message)
                ##
                push_guild_history = []
                target_client_socket_fd = self.mapping[target_client_uid].fileno()
                if "gid" in update_message \
                    and self.conns[target_client_socket_fd] is not None \
                    and int(update_message['gid']) != self.conns[target_client_socket_fd]['gid']:
                    self.conns[target_client_socket_fd]["gid"] = int(update_message['gid'])
                    if int(update_message['gid']):
                        push_guild_history = self.get_guild_history(int(update_message['gid']))
                ##
                response_message = {
                    "type"   : "update",
                    "result" : "ok",
                }
                self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

                ##push guild history
                if len(push_guild_history):
                    self.process_write_message(self.mapping[target_client_uid], 'get_chat ' + json.dumps(push_guild_history))
            else:
                response_message = {
                    "type"   : "update",
                    "result" : "err",
                    "msg"    : "error to fix target"
                }
                self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
        else:
            logging.error("handle update message `%s` error %s", message, client_socket)
            response_message = {
                "type"   : "update",
                "result" : "err",
                "msg"    : "error update message"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

        return ("ok", False)

    def hello(self, client_socket, message):
        """
            hello timestamp
        """
        logging.info("handle hello message `%s`", message)
        result = ("ok", False)
        if self.conns[client_socket.fileno()] is not None:
            self.conns[client_socket.fileno()]["time"] = time.time()
            response_message = {
                "type"   : "hello",
                "result" : "ok"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

        else:
            logging.error("handle hello message `%s` error none %s", message, client_socket)
            response_message = {
                "type"   : "hello",
                "result" : "err",
                "msg"    : "error to fix mapping"
            }
            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
            result = ("error to fix mapping", True)

        return result

    def notice(self, client_socket, message):
        """
            公会通告
            notice {"type":0, "guild":x,"exclude":x, "msg":{详细信息}}
            邮件通告
            notice {"type":1, "target":x,"msg":{详细信息}}
        """
        logging.info("handle notice message `%s`", message)
        notice_message = json.loads(message.decode('utf-8'))
        if int(notice_message["type"]) not in (0, 1):
            logging.error("receive error type chat message `%s`", message)
            error_response_message = json.dumps({
                "type"     : "notice",
                "result"   : "err",
                "msg_type" : notice_message["type"],
                "msg"      : "error type"
            })
            self.process_write_message(client_socket, 'rep ' + error_response_message)
            return ("error chat message type", False)

        if int(notice_message['type']) == 0:
            response_message = {
                "type"     : "notice",
                "result"   : "ok",
                "msg_type" : notice_message["type"],
                }

            self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))
            for conn in self.conns.values():
                print conn
                if conn['uid'].count("system") \
                    or conn['gid'] != int(notice_message['guild']) \
                    or conn['uid'] == str(notice_message['exclude']):
                    continue
                logging.info("response notice message loop `%s`", conn)
                self.process_write_message(conn["socket"], 'get_guild ' + notice_message['msg'])

        elif int(notice_message['type']) == 1:
            target_client_uid = str(notice_message["target"]) if notice_message["target"] else None
            if  target_client_uid is not None and target_client_uid in self.player and target_client_uid in self.mapping:
                logging.info("response notice message to target %s", self.mapping[target_client_uid])
                self.process_write_message(self.mapping[target_client_uid], 'get_message ' + notice_message['msg'])
            else:
                response_message = {
                    "type"     : "notice",
                    "result"   : "err",
                    "msg_type" : notice_message["type"],
                    "msg"      : "error to fix target"
                }
                self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

        return ("ok", False)

    def chat(self, client_socket, message):
        """
            私聊
            chat {"type":0, "target":"1000018","msg":"xxxxxxxxxxxx" }
            公共
            chat {"type":1, "msg":"xxxxxxxxxxxx" }
            公会
            chat {"type":2, "msg":"xxxxxxxxxxxx" }
        """

        logging.info("handle chat message `%s`", message)
        chat_message = json.loads(message.decode('utf-8'))
        if int(chat_message["type"]) not in (0, 1, 2):
            logging.error("receive error type chat message `%s`", message)
            error_response_message = json.dumps({
                "type"     : "chat",
                "result"   : "err",
                "msg_type" : chat_message["type"],
                "msg"      : "error type"
            })
            self.process_write_message(client_socket, 'rep ' + error_response_message)
            return ("error chat message type", False)

        sender_client_fileno = client_socket.fileno()
        sender_client_uid    = self.conns[sender_client_fileno].get("uid", None) if self.conns[sender_client_fileno] else None
        sender_client_gid    = self.conns[sender_client_fileno].get("gid", 0) if self.conns[sender_client_fileno] else 0
        sender_client_player = self.player.get(sender_client_uid, None) if sender_client_uid else None
        if sender_client_uid is None or sender_client_player is None:
            logging.error("receive error uid chat message `%s`, %s, %d", message, client_socket, len(self.conns))
            error_response_message = json.dumps({
                "type"     : "chat",
                "result"   : "err",
                "msg_type" : chat_message["type"],
                "msg"      : "error to fix uid"
            })
            self.process_write_message(client_socket, 'rep ' + error_response_message)
            return ("error chat message uid", False)

        if 0 == sender_client_gid and 2 == int(chat_message['type']) and 0 == sender_client_uid.count("system"):
            error_response_message = json.dumps({
                "type"     : "chat",
                "result"   : "err",
                "msg_type" : chat_message["type"],
                "msg"      : "error to fix gid"
            })
            self.process_write_message(client_socket, 'rep ' + error_response_message)
            return ("error chat message uid", False)

        if int(chat_message["type"]) in (1, 2):
            response_message = json.dumps({
                "type"     : "chat",
                "result"   : "ok",
                "msg_type" : chat_message["type"],
            })
            self.process_write_message(client_socket, 'rep ' + response_message)

            response_message = {
                "type"     : chat_message["type"],
                "sender"   : sender_client_uid if 0 == sender_client_uid.count("system") else "system",
                "name"     : sender_client_player.name,
                "level"    : sender_client_player.level,
                "first"    : sender_client_player.first_name,
                "last"     : sender_client_player.last_name,
                "msg"      : chat_message["msg"],
                "add_time" : chatutil.get_format_time()
            }
            sender_gid = int(chat_message['guild']) if "guild" in chat_message else sender_client_gid
            response   = json.dumps(response_message)
            logging.info("response chat message to all `%s`", response)
            for conn in self.conns.values():
                if conn['uid'].count("system"):
                    continue
                if  2 == chat_message['type'] and conn['gid'] != sender_gid:
                    continue

                logging.info("response chat message loop `%s`", conn)
                self.process_write_message(conn["socket"], 'get_chat ' + response)
            self.add_history(response_message, 0, sender_gid if 2 == chat_message['type'] else 0)
        else:
            target_client_uid = str(chat_message["target"]) if chat_message["target"] else None
            if  target_client_uid is not None and target_client_uid in self.player and target_client_uid in self.mapping:
                response_message = json.dumps({
                    "type"     : "chat",
                    "result"   : "ok",
                    "msg_type" : chat_message["type"],
                })
                self.process_write_message(client_socket, 'rep ' + response_message)
                response_message = {
                    "type"     : chat_message["type"],
                    "sender"   : sender_client_uid,
                    "name"     : sender_client_player.name,
                    "level"    : sender_client_player.level,
                    "first"    : sender_client_player.first_name,
                    "last"     : sender_client_player.last_name,
                    "msg"      : chat_message["msg"],
                    "add_time" : chatutil.get_format_time()
                }
                response = json.dumps(response_message)
                logging.info("response chat message to one `%s`, target %s", response, self.mapping[target_client_uid])
                self.process_write_message(self.mapping[target_client_uid], 'get_chat ' + response)
                self.add_history(response_message, target_client_uid, 0)
            else:
                response_message = {
                    "type"     : "chat",
                    "result"   : "err",
                    "msg_type" : chat_message["type"],
                    "msg"      : "error to fix target"
                }
                self.process_write_message(client_socket, 'rep ' + json.dumps(response_message))

        return ("ok", False)