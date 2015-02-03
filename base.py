#!/usr/bin/env python
# vim:fileencoding=utf-8

import sys


class Base(object):

    """Docstring for Base. """

    def get_headers(self):
        raise NotImplementedError("get_headers must be defined")

    def get_content(self):
        raise NotImplementedError("get_content must be defined")


class BaseWithCookie(Base):

    """Docstring for BaseWithCookie. """

    def __init__(self, cookies_obj=None):
        """TODO: to be defined1. """
        try:
            self.cookies = cookies_obj.str_cookies()
            self.user_id = cookies_obj.get_user_id()
        except Exception as e:
            print u"{}".format(e)
            sys.exit()
