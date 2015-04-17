#-*- coding:utf-8 -*-
from util.text_process import keep_certain_keys
from util.url_fetch import (
        FetchData,
        )
from util.baidu_fetch import (
        BaiduFetchAnalyst,
        )
from db import (
        DBSession,
        )
import copy
import time
import json
import re
import urllib

class BaiduWork(object):
    def __init__(self, channel_api_url='http://news.baidu.com/n',allow_total_page = 2, cmd=4, channel_name='star', **kwargs):
        self.fetch_url = channel_api_url
        self.allow_total_page = allow_total_page
        self.data={}
        self.data['cmd'] = cmd
        self.data['class'] = channel_name
        self.data['pn'] = 1
        self.data.update( kwargs )

    def __call__(self):
        while( self.data['pn'] <= self.allow_total_page ):
            self.fetch_page_data()
            self.data['pn'] = self.data['pn'] + 1

    def fetch_page_data(self):
        query = urllib.urlencode(self.data)
        url = self.fetch_url + '?' + query
        try:
            status_code, self.resp = FetchData.fetch( url, need_status_code=True )
            if status_code in [200,'200']:
                self.process_content()
                self.save_data()
            else:
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
        content = self.resp.decode('gb2312').encode('utf-8')
        self.resp = []
        content = content.replace('\n','')
        one_piece_pattern = '<div>&#[0-9]{4};(.*?)</div>'
        news_list = re.findall(one_piece_pattern, content)
        title_pattern = '<a.*mon="ph".*?target="_blank".*?>(.*?)</a>.*?<span.*?class="c">'
        url_pattern = '<a.*?href="(.*?)".*mon="ph".*?target="_blank".*?>.*?</a>.*?<span.*?class="c">'
        media_name_pattern = '<span.*?class="c">(.*?)&'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            media_name = re.findall( media_name_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            tmp['media_name'] = media_name[0] if media_name else ''
            url = url[0] if url else ''
            tmp['url'] = url
            tmp = self.append_more_info( tmp )
            self.resp.append( tmp )

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        url = tmp['url']
        try:
            res = BaiduFetchAnalyst.fetch( url ) 
            tmp.update( res )
        except Exception, e:
            print e
        finally:
            return tmp

    def reset_fetch_url(self, url):
        self.page = 1
        self.stop_work = False
        self.fetch_url = url
        self.url_template = self.fetch_url+'_{0}.htm?{1}'

    def reset_fetch_data(self, data):
        self.data.update( data )

worker = BaiduWork()
worker()
worker.reset_fetch_data( {'class':'star_chuanwen','pn':1} )
worker()
worker.reset_fetch_data( {'class':'star_gangtai','pn':1} )
worker()
worker.reset_fetch_data( {'class':'star_neidi','pn':1} )
worker()
worker.reset_fetch_data( {'class':'star_oumei','pn':1} )
worker()
worker.reset_fetch_data( {'class':'star_rihan','pn':1} )
worker()
