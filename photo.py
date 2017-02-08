#!/usr/bin/env python
# vim:fileencoding=utf-8

import time
import os
import sys

import requests
from requests.exceptions import Timeout

from api import Cookie, Photo, Albumns

RETRY_NUM = 5


DEFAULT_FOLDER = 'images'


def create_folder(sub_folder, root_folder):
    try:
        folder = os.path.join(root_folder, sub_folder)
        print u"创建目录{}".format(folder)
        os.makedirs(folder)
    except Exception as e:
        print e


def save_file(title, url, sub_folder, root_folder):
    retry_num = RETRY_NUM
    name = u"{}.jpg".format(title)
    file = os.path.join(root_folder, sub_folder, name)
    print u"开始下载: {}".format(name)
    with open(file, "wb") as f:
        while(retry_num):
            try:
                r = requests.get(url, stream=True, timeout=5)
                for chunk in r.iter_content():
                    f.write(chunk)
                time.sleep(0.3)
            except Timeout:
                retry_num -= 1
                continue
            else:
                break


def main(username, passwd, root_folder=DEFAULT_FOLDER):
    cookies_obj = Cookie(username=username, passwd=passwd)
    for sub_folder, album_link in Albumns(cookies_obj=cookies_obj).get():
        create_folder(sub_folder, root_folder)
        r_obj = Photo(cookies_obj=cookies_obj, url=album_link)
        for title, image_link in r_obj.get():
            try:
                save_file(title, image_link, sub_folder, root_folder)
            except Exception as e:
                print e


def add_path():
    package_path = os.path.join(os.path.abspath(__file__), "../..")
    sys.path.append(package_path)


def print_usage():
    print """Usage:
    python2.7 photos.py USER_EMAIL PASSWORD
    """
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage()
    add_path()
    username, passwd = sys.argv[1:]
    main(username, passwd)
