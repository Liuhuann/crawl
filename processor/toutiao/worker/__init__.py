#-*- coding:utf-8 -*-

from util.text_process import keep_certain_keys
from util.url_fetch import (
        FetchData,
        )
from util.baidu_fetch import (
        BaiduFetchAnalyst,
        )
from util.text_process import (
        json_loads_str,
        )
from db import (
        DBSession,
        )
import urllib
import copy
import time
import json
import re

class ToutiaoWorker(object):
    def __init__(self, allow_request_count=200,  **kwargs):
        self.fetch_url = 'http://toutiao.com/api/article/recent/?'
        self.data={}
        self.data['source'] = 2
        self.data['count'] = 20
        self.data['category'] = 'news_entertainment'
        self.data['max_behot_time'] = time.time()
        self.data['utm_source'] = 'toutiao'
        self.data['offset'] = 0
        self.data['_'] = int(time.time()*1000)
        self.data.update( kwargs )
        self.request_count = 0
        self.allow_request_count = allow_request_count

    def __call__(self):
        while( self.request_count < self.allow_request_count ):
            self.fetch_page_data()
            self.request_count = self.request_count + 1

    def fetch_page_data(self):
        self.data['_'] = self.data['_'] + 1
        query = urllib.urlencode( self.data )
        url = self.fetch_url + query
        try:
            print 'list page url is ', url
            self.resp = FetchData.fetch( url )
            if self.check_is_validate_requests_resp():
                self.save_data()
            else:
                print '请求不合法'
        except Exception, e:
            print e
            pass

    def check_is_validate_requests_resp(self):
        """
        判断是不是一个有效的请求返回
        """
        if hasattr(self, 'resp'):
            self.resp  = json_loads_str( self.resp )
            if self.resp and self.resp['message'] in ['success']:
                self.data['_'] = self.data['_'] + 1
                self.resp = self.resp['data']
                return True
            else:
                print 'self. resp status code is not 200'
                return False
        else:
            print 'self does not has attr resp'
            return False

    def save_data(self):
        if self.resp:
            max_create_time = 0
            for item in self.resp:
                tmp = {}
                tmp['keywords'] = item['keywords']
                tmp['images'] = [ image['url'] for image in item['image_list'] ]
                tmp['title'] = item['title']
                tmp['media_name'] = item['source']
                tmp['summary'] = item['abstract']
                tmp['url'] = item['article_url']
                create_time = int(item['create_time'])
                max_create_time = create_time if create_time > max_create_time else max_create_time
                tmp = self.append_more_info( tmp )
                flag = DBSession.save( tmp )
                if not flag:
                    print 'write failed with data=', json.dumps( tmp )
                else:
                    print 'write successed '
            self.data['max_create_time'] = max_create_time
        else:
            print 'error with no self.resp or self.resp is not list type'

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        url = tmp['url']
        try:
            res = BaiduFetchAnalyst.fetch( url ) 
            tmp['text'] = res['text']
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                tmp['images'].append(image)
        except Exception, e:
            print e
        finally:
            return tmp

worker = ToutiaoWorker()
worker()
