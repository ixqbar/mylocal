#!/usr/bin/python
#-*-coding:utf-8-*-

from gevent import monkey;monkey.patch_all()
import gevent
from gevent.queue import Queue,Empty
import logging
import urllib2
import urllib
import time
import sys
import traceback
import json
import MySQLdb
from Crypto.Cipher import AES
from Crypto import Random
import binascii

logging.basicConfig(
    level   = logging.ERROR,
    stream  = sys.stdout,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format   = "[%(asctime)s]%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s:%(message)s"
)

def data_encrypt(plaintext, key=''):
    key     = key if len(key) > 16 else key + (' ' * (16 - len(key)))
    iv      = Random.new().read(AES.block_size)
    header  = 'ok,%d,%d,%d' % (0, len( plaintext), binascii.crc32(plaintext) & 0xffffffff)
    header  = header if len(header) > 32 else header + (' ' * (32 - len(header)))
    text    = header +  plaintext
    text    = text if 0 == len(text) % AES.block_size else text + (' ' * (AES.block_size - len(text) % AES.block_size))
    return iv + AES.new(key, AES.MODE_CBC, iv).encrypt(text)

def data_decrypt(text, key=''):
    key        = key if len(key) > 16 else key + (' ' * (16 - len(key)))
    iv         = text[:16]
    plain_text = AES.new(key,AES.MODE_CBC,iv).decrypt(text[16:])

    return plain_text

class Game(object):

    def __init__(self, msg_queue, start_time, end_flag):
        self.msg_queue  = msg_queue
        self.start_time = start_time
        self.end_flag   = end_flag
        self.post_url   = 'http://10.10.41.42/api/execute'
        #self.proxy()

    def proxy(self):
        proxy  = urllib2.ProxyHandler({'http':'127.0.0.1:8888'})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    def run(self):
        post_data_list = [

        ]
        to_encrypt_request  = False
        to_decrypt_response = True
        while True:
            try:
                player_uid = self.msg_queue.get(timeout=2)
                if player_uid:
                    logging.info("get player_uid %s", player_uid)

                    for tmp_data in post_data_list:
                        post_data  = tmp_data % player_uid
                        if to_encrypt_request:
                            data   = data_encrypt(post_data)
                            result = urllib2.urlopen(self.post_url,data, 30).read()
                        else:
                            result = urllib2.urlopen(self.post_url, urllib.urlencode({"service": post_data}), 30).read()

                        if to_decrypt_response:
                            tmp_result = data_decrypt(result)
                            if len(tmp_result) <= 32:
                                logging.error("get result failure %s,%s", post_data, tmp_result)
                            response = json.loads(tmp_result[32:].strip('\0'))
                            if 0 != response['err_no']:
                                logging.error("get response failure %s,%s", post_data, response)

                            logging.info("%s,%s",post_data, response)
                        else:
                            response = json.loads(result)
                            if 0 != response['err_no']:
                                logging.error("get response failure %s,%s", post_data, response)

                            logging.info("%s,%s",post_data, response)

                    if player_uid == self.end_flag:
                        logging.error("stress end %d", time.time() - self.start_time)
                        break
                else:
                    break
            except Empty:
                break
            except:
                logging.error(traceback.format_exc())
                break;


def get_player_uids():
    conn   = MySQLdb.connect("10.10.41.107", "", "", "", charset='utf8')
    cursor = conn.cursor()
    cursor.execute("")
    rows = cursor.fetchall()

    player_uids = []
    for player in rows:
        player_uids.append(player)

    return player_uids

def stress_test():
    start_time  = time.time()
    msg_queue   = Queue()
    spawn_list  = []
    player_uids = get_player_uids()
    end_flag    = player_uids[-1]

    logging.info("total player %d", len(player_uids))

    for x in range(50):
        m = Game(msg_queue, start_time, end_flag)
        spawn_list.append(gevent.spawn(m.run))

    for uid in player_uids:
        msg_queue.put(uid)

    gevent.joinall(spawn_list)

    logging.info('end');

if __name__ == "__main__":
    try:
        stress_test()
    except:
        pass

