#!/usr/bin/python
#-*-coding:utf-8-*-

def ms2():

    file = open("./tmp.log", "w");
    loop = 1
    while True:
        if loop <= 2:
            print >>file, "%d" % (loop, )
            loop += 1
        else:
            break;

    file.close()

    with open('./tmp.log') as file:
        while True:
            line = file.readline()
            if not line:
                break

            print line



if __name__ == '__main__':
    try:
        ms2()
    except Exception as e:
        print e
