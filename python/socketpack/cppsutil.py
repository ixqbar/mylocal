#-*-coding:utf-8-*-

import logging
import socket
import errno
import struct


FATAL_ERROR_NO  = (errno.EBADF, errno.EINVAL, errno.ENOTSOCK)
IGNORE_ERROR_NO = (errno.EAGAIN, errno.EWOULDBLOCK)


def read_sock_buf(sock, buf_len=4, is_header=True):
    buf = ""

    while True:
        try:
            tmp_buf = sock.recv(buf_len)
        except socket.error as err:
            if err.args[0] not in IGNORE_ERROR_NO:
                logging.error("read socket error `%s`, `%s`" % (err, sock,))
                break;

        if 0 == len(tmp_buf):
            break;

        buf += tmp_buf
        if len(tmp_buf) == buf_len:
            logging.debug("read header over header_buff `%s`" % (buf, ))
            break;
        else:
            buf_len -= len(tmp_buf)
            logging.debug("read header loop next read len `%d`" % (buf_len,))

    if len(buf) == 0:
        return (False, "socket `%s` disconnected" % (sock,))
    elif is_header:
        data_len = struct.unpack('!i', buf)
        logging.debug("header `%s` begin to read body buf", buf)
        return read_sock_buf(sock, data_len[0], False)
    elif len(buf):
        return (True, buf)
    else:
        return (False, "error buf end flag `%s`" % (buf, ))

def write_sock_buf(sock, buf):
    buf     = struct.pack("!i%ss" % (len(buf),), len(buf), buf)
    buf_len = len(buf)
    start   = 0
    while True:
        try:
            start += sock.send(buf[start:])
        except socket.error as err:
            if err.args[0] not in IGNORE_ERROR_NO:
                return (False, "socket error")

        if start == buf_len:
            break;

    return (True, "")
