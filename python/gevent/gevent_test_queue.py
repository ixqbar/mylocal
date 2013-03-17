#-*-coding:utf-8-*-

import gevent
from gevent.queue import Queue

tasks = Queue()

def worker(n):
    while True:
        task = tasks.get()
        if task:
            print('Worker %s got task %s' % (n, task))
        #很重要哦，不然切换不到其他worker
        gevent.sleep(0)


    print('Quitting time!')

def boss():
    for i in xrange(1,25):
        tasks.put_nowait(i)

gevent.joinall([
    gevent.spawn(worker, 'steve'),
    gevent.spawn(worker, 'john'),
    gevent.spawn(worker, 'nancy'),
    gevent.spawn(boss)
    ])




