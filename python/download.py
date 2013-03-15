
import os
import time
import logging
import urllib
import hashlib
import threading
import Queue

logging.basicConfig(
    level   = logging.INFO,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format  = "[%(asctime)s]%(levelname)s-%(filename)s-%(funcName)s-%(lineno)s:%(message)s"
)

# tmp_url = "http://wyx-dev.break.sh.cn/res/Main.swf"
# urllib.urlretrieve(tmp_url, "./test.swf")

# for path,dirs,filenames in os.walk("/home/venkman/wwwroot/www.horror.com/"):
#     print(path,dirs,filenames)

# try:
#     os.mkdir("./test")
# except Exception as e:
#     #(17, 'File exists')
#     print(e.args)


local_cdn_path = "/home/venkman/PycharmProjects/email/cdn/"
route_cdn_url  = "http://swf.games.sina.com.cn/ryxz/13031301/"
local_path     = os.getcwd() + "/" + time.strftime("%Y%m%d") + "/"

def easy_mkdir(mk_path):
    """
    @TODO
    """
    try:
        if isinstance(mk_path, str):
            if not os.path.exists(mk_path):
                os.makedirs(mk_path)
        else:
            for tmp_path in mk_path:
                if not os.path.exists(tmp_path):
                    os.makedirs(tmp_path)
    except Exception as e:
        logging.exception(e.args)

def easy_tree():
    """
    @TODO
    """
    all_paths      = []
    all_files      = []
    start_position = len(local_cdn_path)
    file_m         = hashlib.md5()

    for path,dirs,files in os.walk(local_cdn_path):
        if ".svn" in path:
            continue

        child_path_name = path[start_position:]
        for child_file in files:
            f = open(path + "/" + child_file, "rb")
            file_m.update(f.read(os.path.getsize(path + "/" + child_file)))
            if child_path_name:
                all_files.append((route_cdn_url + child_path_name + "/" + child_file, file_m.hexdigest()))
            else:
                all_files.append((route_cdn_url + child_file, file_m.hexdigest()))
            f.close()

        for child_dir in dirs:
            if ".svn" == child_dir:
                continue

            if child_path_name:
                all_paths.append(local_path + child_path_name + "/" + child_dir)
            else:
                all_paths.append(local_path + child_dir)

    return (all_paths, all_files)


class Download(threading.Thread):
    """
    @TODo
    """

    def __init__(self, route_cdn_url, local_path, download_queue):
        threading.Thread.__init__(self)
        self.start_position     = len(route_cdn_url)
        self.local_path         = local_path
        self.download_queue     = download_queue
        self.url_opener         = urllib.FancyURLopener()
        self.url_opener.version = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:19.0) Gecko/20100101 Firefox/19.0"

    def run(self):

        while True:
            try:
                url = self.download_queue.get(True, 3)
                if url:
                    tmp_file       = url[self.start_position:]
                    download_file  = self.local_path + tmp_file
                    tmp_dirs       = tmp_file.split("/")
                    easy_mkdir(self.local_path + "/".join(tmp_dirs[:-1]))
                    logging.info("start downloading `%s` to `%s`", tmp_file, download_file)
                    self.url_opener.retrieve(url, download_file)
                    url = None
            except Queue.Empty as e:
                break
            except Exception as e:
                logging.exception(e.args)
                if url:
                    logging.warning("retry downloading `%s` to `%s`", tmp_file, download_file)
                    self.download_queue.put(url)


def easy_download(all_files):
    download_queue = Queue.Queue()
    for file in all_files:
        if file:
            download_queue.put(file[0])

    all_threads = [];
    for i in xrange(100):
        t = Download(route_cdn_url,local_path,download_queue)
        t.start()
        all_threads.append(t)

    for t in all_threads:
        t.join()


if __name__ == '__main__':
    try:
        all_paths, all_files = easy_tree()
        easy_mkdir(local_path)
        #easy_mkdir(all_paths)
        easy_download(all_files)
    except Exception as e:
        logging.exception(e)
