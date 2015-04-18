# -*- coding:utf-8 -*-
import requests

class FetchData(object):
    @classmethod
    def fetch(cls, url, need_status_code=False):
        res = None
        try:
            resp = requests.get(url)
            if not need_status_code:
                if int(resp.status_code) in [200]:      
                    res = resp.content
                else:
                    res = None
            else:
                res = (resp.status_code, resp.content)
        except Exception,e:
            print e
            if not need_status_code:
                res = None
            else:
                res = (500, None)
        finally:
            return res
