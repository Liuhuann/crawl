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

class QQWork(object):
    def __init__(self, channel_api_url='', domain='http://ent.qq.com', **kwargs):
        self.fetch_url = channel_api_url
        self.url_template = self.fetch_url+'_{0}.htm?{1}'
        self.domain = domain
        self.stop_work = False
        self.page = 1
        self.data={}
        self.data.update( kwargs )

    def __call__(self):
        while( not self.stop_work ):
            self.fetch_page_data()
            self.page = self.page + 1

    def fetch_page_data(self):
        a=time.time()
        a=a/10000000000
        url = self.url_template.format(self.page,a)
        print 'url is ', url
        try:
            status_code, self.resp = FetchData.fetch( url, need_status_code=True )
            if status_code in [200,'200']:
                self.process_content()
                self.save_data()
            else:
                print '请求不合法'
                self.stop_work = True
        except Exception, e:
            print e
            pass

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
        one_piece_pattern = '<div class="nrC">(.*?)<div class="subInfo">'
        news_list = re.findall(one_piece_pattern, content)
        small_img_pattern = '<img.*?class="nrPic".*?src="(.*?)" alt=.*?">'
        title_pattern = '<a.*target="_blank".*?class="newsTit".*?href=".*?">(.*?)</a></h3>'
        intro_pattern = '<div.*?class="nrP">(.*?)<a.*?>全文'
        url_pattern = '<a.*?class="detail".*?href="(.*?)">全文</a>'
        media_name_pattern = '<p.*?class="newsInfo".*?>(.*?)<span.*?class="date".*?>'
        for item in news_list:
            img = re.findall( small_img_pattern , item )
            title = re.findall( title_pattern, item )
            intro = re.findall( intro_pattern, item )
            url = re.findall( url_pattern, item )
            media_name = re.findall( media_name_pattern, item )
            tmp = {}
            tmp['img'] = img
            tmp['title'] = title[0] if title else ''
            tmp['waptitle'] = ''
            tmp['intro'] = intro[0] if intro else ''
            tmp['summary'] = tmp['intro']
            tmp['media_name'] = media_name[0] if media_name else ''
            url = url[0] if url else ''
            url = self.domain + url if url and url.startswith('/a') else ''
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


worker = QQWork('http://ent.qq.com/c/wbbl')
worker()
worker.reset_fetch_url('http://ent.qq.com/c/mxzx')
worker()
worker.reset_fetch_url('http://ent.qq.com/c/dlxw')
worker()
worker.reset_fetch_url('http://ent.qq.com/c/omxwn')
worker()
worker.reset_fetch_url('http://ent.qq.com/c/txdj')
worker()
