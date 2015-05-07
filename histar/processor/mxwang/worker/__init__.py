#-*- coding:utf-8 -*-
from histar.util.text_process import(
        keep_certain_keys,
        reformat_date_str,
        )
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

class MXWWork(object):
    def __init__(self, page_limit=True, total_page_count=3010, page = 1 ):
        self.stop_work = False
        self.fetch_url = 'http://news.mingxing.com/star/'
        self.fetch_format_url = self.fetch_url
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page

    def __call__(self):
        while( self.page <= self.total_page_count and not self.stop_work):
            self.fetch_page_data()
            self.page = self.page + 1

    def fetch_page_data(self):
        if self.page == 1:
            url = self.fetch_url
        else:
            url = self.fetch_url + 'index_' + str(self.page) + '.html'
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
        try:
            content = self.resp.decode('utf-8')
        except Exception, e:
            content = self.resp
        self.resp = []
        content = content.replace('\n','')
        content = content.replace("'",'"')

        one_piece_pattern = '(<li><span class="img">.*?</li>)'
        url_pattern ='<h3 class="txt01"><a href="(.*?)".*>'
        title_pattern = '<h3 class="txt01"><a .*>(.*)</a>'
        publish_ts_pattern = '<span class="txt02">(.*)</span>'
        
        news_list = re.findall(one_piece_pattern,content)
        print len(news_list)

        if len(news_list)==0:
            self.stop_work = True

        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            publish_ts = re.findall( publish_ts_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url   
            publish_ts = publish_ts[0] if publish_ts else ''
            tmp['publish_ts'] = reformat_date_str( publish_ts )
            tmp['text'] = []
            tmp['media_name'] = u'明星网'
            tmp = self.append_more_info( tmp )
            print '***********************************'
            print tmp['publish_ts']
            print tmp['title']
            print tmp['url']
            for item in tmp['text']:
                print item['type'],
                print item['data']
            print '***********************************'
            break
            self.resp.append( tmp )

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """

        url = tmp['url']
        try:
            res = BaiduFetchAnalyst.fetch( url )
            tmp['text'] = res['text']
        
        except Exception, e:
            print e
        finally:
            return tmp

if __name__ =="__main__":
    worker = MXWWork(total_page_count=1)
    worker()

