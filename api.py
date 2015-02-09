#!/usr/bin/env python
# vim:fileencoding=utf-8

import json
import re

import requests

from renren_album.base import Base, BaseWithCookie
from renren_album.encrypt import encryptString

REG = re.compile("'albumList': (.*),")
LOGIN = ("http://www.renren.com/ajaxLogin/login"
         "?1=1&uniqueTimestamp=2015111859588")


class Cookie(Base):

    """Docstring for CreateCookie2. """

    def __init__(self, username="", passwd=""):
        """TODO: to be defined1. """
        self.url = LOGIN
        self.username = username
        self.passwd = self.get_passwd(passwd)
        self._cookies = None

    def get_headers(self):
        r = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http//www.renren.com",
            "Referer": "http://www.renren.com/SysHome.do",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0\
                    like Mac OS X; en-us) AppleWebKit/537.51.1 (K\
                    HTML, like Gecko) Version/7.0 Mobile/11A465 Sa\
                    fari/9537.53",
            "X-Requested-With": "XMLHttpRequest",
        }
        return r

    def get_passwd(self, raw_passwd):
        # TODO: 这是一个密码加密的地方，貌似是MD5
        r = requests.get("http://login.renren.com/ajax/getEncryptKey").text
        rr = json.loads(r)
        self.rkey = rr["rkey"]
        n = rr["n"]
        e = "10001"
        return encryptString(e, n, raw_passwd)

    def get_data(self):
        d = {
            "email": self.username,
            "icode": "",
            "origURL": "http://www.renren.com/home",
            "domain": "renren.com",
            "key_id": "1",
            "captcha_type": "web_login",
            "password": self.passwd,
            "rkey": self.rkey,
            "f": "http%3A%2F%2Fwww.renren.com%2F222445084",
        }
        return d

    def get_content(self):
        kwargs = {}
        kwargs["headers"] = self.get_headers()
        kwargs["data"] = self.get_data()
        kwargs["allow_redirects"] = True
        return requests.post(self.url, **kwargs)

    @property
    def cookies(self):
        if not self._cookies:
            r = self.get_content()
            r_dict = json.loads(r.text)
            if not r_dict["code"]:
                raise Exception(
                    u"获取cookie失败：{}".format(r_dict["failDescription"]))
            if json.loads(r.text).get("code"):
                self._cookies = r.cookies
        return self._cookies

    def str_cookies(self):
        l = ["{}={}".format(k, v) for k, v in self.cookies.items()]
        return "; ".join(l)

    def get_user_id(self):
        return self.cookies["id"]


class Albumns(BaseWithCookie):

    """Docstring for Albumns. """

    def __init__(self, cookies_obj):
        """TODO: to be defined1. """
        super(Albumns, self).__init__(cookies_obj=cookies_obj)
        self.headers = self.get_headers()

    def get_headers(self):
        h = {
            "Host": "photo.renren.com",
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS "
                           "X 10.10; rv:35.0) Gecko/20100101 Fire"
                           "fox/35.0"),
            "Accept": ("application/json, text/javascript, */*; q="
                       "0.01"),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookies,
        }
        return h

    def get_url(self):
        return "http://photo.renren.com/photo/{}/albumlist/v7".\
            format(self.user_id)

    def get_content(self):
        r = requests.get(self.get_url(), headers=self.headers)
        if r.status_code != 200:
            raise Exception("Return code error, %s" % r.status_code)
        raw = r.text
        return json.loads(re.search(REG, raw).groups()[0])

    def get(self):
        raw = self.get_content()
        albumId = map(lambda x: x["albumId"], raw)
        albumName = map(lambda x: x["albumName"], raw)
        do_filter = lambda x: "http://photo.renren.com/photo/{}/album-{}/list".\
            format(self.user_id, x)
        url = map(do_filter, albumId)
        return zip(albumName, url)


class Photo(Albumns):

    """Docstring for Photo. """

    def __init__(self, cookies_obj=None, url=None):
        super(Photo, self).__init__(cookies_obj=cookies_obj)
        self.url = url

    def get_content(self):
        r = requests.get(self.url, headers=self.headers)
        if r.status_code != 200:
            raise Exception("Return code error, %s" % r.status_code)
        return r.text

    def get(self):
        raw = self.get_content()
        raw = json.loads(raw)["list"]
        url = map(lambda x: x["largeUrl"], raw)
        name = map(lambda x: x.get("originTitle", "unname"), raw)

        def do_filter(x):
            if not x.split("/")[-1].startswith("p_"):
                return x.replace("large", "original")
            return x
        url = map(do_filter, url)
        return zip(name, url)
