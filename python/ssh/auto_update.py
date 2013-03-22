#!/usr/bin/python
#-*-coding:utf-8-*-
#
#
#
#
#vim ~/.bashrc
#alias upsinadev=`python [PATH]/auto_update.py sina_dev`
#
#

import sys
import traceback
import paramiko

def auto_update(platform):
    """@TODO"""

    platform_list = {
        'sina_dev' : {
            'connect_params':{'hostname':'10.10.41.102','username':'root','password':''},
            'command':'svn up /data/wwwroot/sina_dev/'
        },
        'sina_qa' : {
            'connect_params':{'hostname':'10.10.41.102','username':'root','password':''},
            'command':'svn up /data/wwwroot/sina_qa/'
        },
        'jp_dev' : {
            'connect_params':{'hostname':'10.10.41.102','username':'root','password':''},
            'command':'svn up /data/wwwroot/jp_dev/'
        },
        'jp_rw' : {
            'connect_params':{'hostname':'10.10.41.101','username':'root','password':''},
            'command':'svn up /data/wwwroot/jp_rw/'
        }
    }

    if not platform in platform_list:
        return False

    ssh_handle = paramiko.SSHClient()
    ssh_handle.load_system_host_keys()
    ssh_handle.connect(**platform_list[platform]['connect_params'])
    result = ssh_handle.exec_command(platform_list[platform]['command'])
    print result[1].read()
    ssh_handle.close()

    return True

if __name__ == "__main__":
    try:
        auto_update("jp_rw")
        if 2 ==len(sys.argv):
            auto_update(sys.argv[1])
        else:
            print("You must usage like `%s` platform_name" % (sys.argv[0],))
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

    sys.exit(0)
