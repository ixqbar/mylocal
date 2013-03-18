
import gevent


def test1():
    gevent.sleep(1);
    print "test1"


def test2():
    print "test2"
    gevent.sleep(10);
    print "test2 end"


gevent.joinall([
    gevent.spawn(test1),
    gevent.spawn(test2)
])