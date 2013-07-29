#!/bin/python
#-*-coding:utf-8-*-

import struct
import urllib
import sys
import os

def parse(bi_file):
    with open(bi_file) as file:
        while True:
            line = file.readline().strip()
            if not line:
                break

            result = struct.unpack("!iii50shhhhhhhhhhh", line[0:84])
            bi = {
                'server_timestamp' : result[0],
                'request_timestamp': result[1],
                'event'            : result[2],
                'uid'              : result[3].strip('0'),
                'params'           : []
            }

            offset = 84
            for p_len in result[5:]:
                if p_len:
                    p = (struct.unpack("%ds" % (p_len,), line[offset:offset + p_len]))
                    bi['params'].append(urllib.unquote(p[0]).decode('utf8'))
                    offset += p_len
                else:
                    bi['params'].append("")

            yield bi

def test(bi_file):
    if os.path.exists(bi_file) == False:
        raise "no exists %s" % (bi_file, )

    for p in parse(bi_file):
        print p

if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
            test(sys.argv[1])
        else:
            print ("You must uage like `python %s bi_file`" % (sys.argv[0], ))
    except Exception as e:
        print e.message