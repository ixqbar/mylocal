
import gevent

i=0;

def test1():
    global i
    i = i + 1
    print "test1 ", i


def test2():
    global i
    i = i + 1
    print "test2 ", i

def test3():
    global i
    i = i + 1
    print "test3 ", i

def test4():
    global i
    i = i + 1
    print "test4 ", i

def test5():
    global i
    i = i + 1
    print "test5 ", i

gevent.joinall([
    gevent.spawn(test1),
    gevent.spawn(test2),
    gevent.spawn(test3),
    gevent.spawn(test4),
    gevent.spawn(test5),
])