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
import copy
import time
import json
import re
import urllib

class XinhuaWork(object):
    def __init__(self, past_news_need=False, page_limit=False, total_page_count=100, channelid='223342', prepage=40, _list='', searchword="extend5='%116716%'"):
        self.stop_work = False
        self.fetch_url = 'http://203.192.8.57/was5/web/search'
        self.today_new_url = 'http://www.news.cn/ent/mx.htm'
        self.data = {}
        self.data['channelid'] = channelid
        self.data['prepage'] = prepage
        self.data['list'] = _list
        self.data['page'] = 1
        self.data['searchword'] = searchword
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.past_news_need = past_news_need
        

    def __call__(self):
        if True:
            self.fetch_past_news()
        #self.fetch_today_news()

    def fetch_today_news(self):
        status_code , self.resp = FetchData.fetch(self.today_new_url, need_status_code=True)
        if status_code in ['200',200]:
            self.process_today_news_content()
            self.save_data()
            
    def process_today_news_content(self):
        content = self.resp
        content = content.replace('\n','')
        one_piece_pattern = '<li.*?class="clearfix">(.*?)</li>'
        title_pattern = '<h3><a.*?>(.*?)</a>.*?</h3>'
        url_pattern = '<h3><a.*href="(.*?)".*?>.*?</a>.*?</h3>'
        summary_pattern = '<p.*?class="summary">(.*?)</p>'
        img_pattern = '<img.*?class="lazyload".*?data-original=(.*?)/>'
        news_list = re.findall( one_piece_pattern, content )
        self.resp = []
        if len(news_list)==0:
            self.stop_work = True
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            summary = re.findall( summary_pattern, item )
            img = re.findall( img_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            tmp['url'] = url[0] if url else ''
            tmp['summary'] = summary[0] if summary else ''
            tmp['img'] = img
            tmp = self.append_more_info(tmp)
            self.resp.append( tmp )

    def fetch_past_news(self):
        while( not self.stop_work ):
            self.fetch_page_data()
            self.data['page'] = self.data['page'] + 1
            if self.page_limit:
                if self.data['page'] >= self.total_page_count:
                    self.stop_work = True
    
    def fetch_page_data(self):
        query = urllib.urlencode(self.data)
        url = self.fetch_url + '?' + query
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
        one_piece_pattern = '<li>(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<a.*?target="_blank">(.+?)</a>'
        url_pattern = '<a.*?href="(.+?)".*?target="_blank">.+?</a>'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
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
            tmp['text'] = res['text']
            if res.get('media_name',""):
                tmp['media_name'] = res['media_name']
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                if image not in tmp['images']:
                    tmp['images'].append(image)
            status, res = FetchData.fetch(url, need_status_code = True )
            if status in ['200',200]:
                res = res.lower()
                res = res.replace('年','-')
                res = res.replace('月','-')
                res = res.replace('日 ',' ')
                res = res.replace('日',' ')
                pa = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2})'
                l = re.findall(pa, res, re.MULTILINE)
                if len(l) ==1:
                    tmp['publish_ts'] = l[0]
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

if __name__ =="__main__":
    worker = XinhuaWork(past_news_need=True, total_page_count=51, page_limit=True)
    worker()
