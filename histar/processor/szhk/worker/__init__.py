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

class SZHKWork(object):
    def __init__(self, page_limit=True, total_page_count=1, page = 1):
        self.stop_work = False
        self.domain = 'http://yl.szhk.com/starnews/'
        self.fetch_url = ''
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page
        self.channels = ['mainland','hk_tw','international','oumei']

    def __call__(self):
        for channel in self.channels:
            self.page = 1
            self.fetch_url = self.domain + channel
            while( self.page <= self.total_page_count and not self.stop_work):
                self.fetch_page_data()
                self.page = self.page + 1

    def fetch_page_data(self):
        url = self.fetch_url
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
        index = content.find('<ul class="sznews_list">')
        if index >=0:
            content = content[index:]
            index = content.find('<div class="page"')
            content = content[:index]
            content = content.replace('年','-')
            content = content.replace('月','-')
            content = content.replace('日','')
        else:
            return
        one_piece_pattern = '<li>(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = 'title="(.*?)"'
        url_pattern = 'href="(.*?)"'
        ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2})'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            ts = re.findall( ts_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url if url.startswith('http') else self.fetch_url + url
            tmp['publish_ts'] = ts[0] if ts else ''
            tmp['text'] = []
            tmp['media_name'] = u'深港在线'
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
    worker = SZHKWork()
    worker()
