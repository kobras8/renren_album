#!/usr/bin/env python
# vim:fileencoding=utf-8

import time
import os

import requests
from requests.exceptions import Timeout

from renren_pic.api import Cookie, Photo, Albumns

ROOT = u"/Users/kobras/Pictures/相册/人人网/"
RETRY_NUM = 5


def create_folder(sub_folder):
    try:
        folder = os.path.join(ROOT, sub_folder)
        print u"创建目录{}".format(folder)
        os.makedirs(folder)
    except Exception as e:
        print e


def save_file(title, url, sub_folder):
    retry_num = RETRY_NUM
    name = u"{}.jpg".format(title)
    file = os.path.join(ROOT, sub_folder, name)
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


def main(username, passwd):
    cookies_obj = Cookie(username=username, passwd=passwd)
    for sub_folder, album_link in Albumns(cookies_obj=cookies_obj).get():
        create_folder(sub_folder)
        r_obj = Photo(cookies_obj=cookies_obj, url=album_link)
        for title, image_link in r_obj.get():
            try:
                save_file(title, image_link, sub_folder)
            except Exception as e:
                print e


if __name__ == '__main__':
    main("xxxx@163.com", "")
