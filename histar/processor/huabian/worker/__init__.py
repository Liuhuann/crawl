#-*- coding:utf-8 -*-
from histar.util.text_process import keep_certain_keys
from histar.util.url_fetch import (
        FetchData,
        )
from histar.util.baidu_fetch import (
        BaiduFetchAnalyst,
        )
from histar.db import (
        DBSession,
        )
from datetime import (
        datetime,
        timedelta,
        )
import copy
import time
import json
import re
import urllib

class HuabianWork(object):
    def __init__(self, page_limit=True, total_page_count=5814, page = 1):
        self.stop_work = False
        self.fetch_url = 'http://www.huabian.com/xingwen/{0}.html'
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page

    def __call__(self):
        while( self.page <= self.total_page_count and not self.stop_work):
            self.fetch_page_data()
            self.page = self.page + 1

    def fetch_page_data(self):
        url = self.fetch_url.format(self.page)
        try:
            print 'url is ', url
            status_code, self.resp = FetchData.fetch( url, need_status_code=True )
            if status_code in [200,'200']:
                self.process_content()
                self.save_data()
            else:
                print 'status code 不合法，自动停止'
                print '请求不合法'
        except Exception, e:
            print e

    def save_data(self):
        if self.resp:
            for item in self.resp:
                flag = DBSession.save( item )
                if not flag:
                    print 'write failed with data=', json.dumps( item )
                else:
                    print 'write successed '
        else:
            print 'error with no self.resp or self.resp is not list type'

    def process_content(self):
        content = self.resp
        self.resp = []
        content = content.replace('\n','')
        content = content.replace("'",'"')
        one_piece_pattern = '<div class="box">(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<div class="title"><a href=".*?".*?>(.*?)</a>'
        url_pattern = '<div class="title"><a href="(.*?)".*?>.*?</a>'
        summary_pattern = '<div class="txt">(.*?)<a href'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            summary = re.findall( summary_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url if url.startswith('http') else self.fetch_url + url
            tmp['summary'] = summary[0] if summary else ''
            tmp['text'] = []
            tmp['media_name'] = u'花边星闻'
            tmp = self.append_more_info( tmp )
            print '***********************************'
            print tmp['publish_ts']
            #for item in tmp['text']:
            #    print item['type'],
            #    print item['data']
            print '***********************************'
            self.resp.append( tmp )

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        
        url = tmp['url']
        print 'detail url is ', url
        try:
            baidu = BaiduFetchAnalyst.fetch( url )
            tmp['images'] = baidu['images']
            tmp['text'] = baidu['text']
            status, res = FetchData.fetch( url, need_status_code=True ) 
            res = res.decode('utf-8')
            if status in ['200',200]:
                res = res.replace('\n','')
                res = res.replace("'",'"')
                ts_patten = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}).*?&nbsp;'
                ts = re.findall( ts_patten, res )
                print ts
                if ts:
                    tmp['publish_ts'] = ts[0]
            else:
                print 'get detail page status code is not 200', url
        except Exception, e:
            print e
        finally:
            return tmp

    def process_publish_ts(self, ts):
        now = datetime.now()
        if ts.find('分钟前') >=0:
            index = ts.find('分钟前')
            ts = ts[:index]
            ts = ts.strip()
            if ts.isdigit():
                return (now-timedelta(minutes=int(ts))).strftime('%Y-%m-%d %H:%M:%S')
            else:
                print 'ts is ', ts
        elif ts.find('小时前') >=0:
            index = ts.find('小时前')
            ts = ts[:index]
            ts = ts.strip()
            if ts.isdigit():
                return (now-timedelta(hours=int(ts))).strftime('%Y-%m-%d %H:%M:%S')
            else:
                print 'ts is ', ts
        elif ts.find('昨天') >=0:
            ts = ts.strip()
            if ts.isdigit():
                return (now-timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                print 'ts is ', ts
        elif ts.find('年') >=0:
            ts = ts.strip()
            ts = ts.replace('年','-')
            ts = ts.replace('月','-')
            ts = ts.replace('日','')
            return ts
        elif ts.find('月') >=0:
            ts = ts.strip()
            ts = ts.replace('月','-')
            ts = ts.replace('日','')
            return '2015-'+ts

if __name__ =="__main__":
    worker = HuabianWork(total_page_count=1571)
    worker()
