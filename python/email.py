#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import time
import redis
import logging
import smtplib
from email.mime.text import MIMEText

logging.basicConfig(
    level   = logging.INFO,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format  = "[%(asctime)s]%(levelname)8s-%(filename)15s-%(funcName)30s-%(lineno)5s:%(message)s"
)

setting = {
    "redis_host"  : "10.10.41.42",
    "redis_port"  : 6379,
    "redis_db"    : 15,
    "target_list" : [],    									#待发送邮件列表
    "mail_host"   : "smtp.163.com",                         #host
    "mail_user"   : "",                              		#user
    "mail_pass"   : "",                             		#password
    "mail_suffix" : "163.com"                               #mail
}

class ServerInfo(object):

    def __init__(self):
        pass

    def send_mail(self, subject, content):
        """

        """

        from_addr = setting["mail_user"] + "<" + setting["mail_user"] +"@" + setting["mail_suffix"] + ">"
        to_addrs  = setting["target_list"]

        text = MIMEText(content)
        text['Subject'] = subject
        text['From']    = from_addr
        text['To']      = ";".join(to_addrs)

        message = text.as_string()
        try:
            s = smtplib.SMTP()
            s.connect(setting["mail_host"])
            s.login(setting["mail_user"], setting["mail_pass"])
            s.sendmail(from_addr, to_addrs, message)
            s.close()
        except Exception as e:
            logging.exception(e)
            return False

        logging.info("send mail success")
        return True

    def deparse_medal_rank(self, score):
        score = str(score)
        return (int(score[:6])-100000, int(score[6:10]))

    def run(self):
        redis_handle    = redis.StrictRedis(host=setting["redis_host"], port=setting["redis_port"], db=setting["redis_db"])
        medal_rank_list = redis_handle.zrevrangebyscore("player_medal_rank:{0}".format(1 + int(time.strftime("%Y%W"))), "+inf", 0, start=0,num=100, withscores=True)
        content         = []
        position        = 1
        for hc_id,score in medal_rank_list:
            medal,level = self.deparse_medal_rank(score)
            player_info = redis_handle.hmget("player:" + hc_id, "name")
            if player_info:
                player_name = player_info[0].decode("utf-8") if player_info[0] and len(player_info[0]) else ""
                content.append("%+3s|%+10s|%+6s|%+5s|%-s" % (position, hc_id, medal, level, player_name))
            else:
                logging.error("player `%s` no name", hc_id)
            position    += 1

        return self.send_mail("%s排行信息" % (time.strftime("%Y-%m-%d"),), "\n".join(content).encode("utf-8"))

if __name__ == '__main__':
    try:
        os.environ["TZ"] = "UTC"
        time.tzset()
        server = ServerInfo()
        server.run()
    except Exception as e:
        logging.exception(e)
