# -*- coding:utf-8 -*-
import requests
import re

class FetchData(object):
    @classmethod
    def fetch(cls, url, need_status_code=False):
        res = None
        try:
            proxy = {'http':'119.254.164.4:30082'}
            headers = {'Referer':'http://news.dzyule.com/'}
            headers['User-Agent']="Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
            resp = requests.get(url, headers=headers, proxies=proxy)
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

    @classmethod
    def find_publish_ts(cls, url):
        status , res = cls.fetch( url, need_status_code=True )
        if status not in ['200',200]:
            return ''
        else:
            res = res.lower()
            index = res.find('body')
            print index
            if index <0 :
                return ''
            res = res[index:]
            res = res.replace('\n','')
            res = res.replace('年','-')
            res = res.replace('月','-')
            res = res.replace('/','-')
            res = res.replace('.','-')
            res = res.replace('日 ','')
            res = res.replace('日',' ')
            pa = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2})'
            ts = re.findall(pa, res)
            publish_ts = ''
            length = len( ts )
            if length == 1:
                print '找到标准的时间格式'
                publish_ts = ts[0]
            elif length == 0:
                print '没有找到标准的时间格式'
            else:
                print '找到多余两个的时间格式'
                publish_ts = ts[0]
            if publish_ts.count('-') == 1:
                publish_ts = '2015-'+publish_ts
            print publish_ts
            l = re.split('-| |:', publish_ts)
            publish_ts = ''
            year = l[0] 
            if len(year) in [1,2]:
                publish_ts = '20'+year
            for item in l[1:3]:
                if len(item) == 1:
                    item = '0'+item
                publish_ts = publish_ts + '-' + item
            publish_ts = publish_ts + ' ' if len(l) == 3 else publish_ts
            for item in l[3:]:
                publish_ts = publish_ts + ':' + item
            return publish_ts

if __name__ == '__main__':
    print FetchData.find_publish_ts('http://news.xinhuanet.com/ent/2015-04/20/c_127708117_2.htm')
