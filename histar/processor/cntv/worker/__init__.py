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

class CNTVWork(object):
    def __init__(self, page_limit=True, total_page_count=1, page = 1):
        self.stop_work = False
        self.domain = 'http://ent.cntv.cn/mingxing/{0}/index.shtml'
        self.fetch_url = ''
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page
        self.channels = ['01','02']

    def __call__(self):
        for channel in self.channels:
            self.page = 1
            self.fetch_url = self.domain.format(channel)
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
        one_piece_pattern = '<li style="display:none;"(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<a.*?href=.*?>(.*?)</a>'
        url_pattern = 'href="(.*?)"'
        ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})'
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
            tmp['media_name'] = u'央视网'
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

class CNTVStarImageWork(object):
    def __init__(self, page_limit=True, total_page_count=1, page = 1):
        self.stop_work = False
        self.domain = 'http://ent.cntv.cn/picture/{0}/index.shtml'
        self.fetch_url = ''
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page
        self.channels = ['01','02']

    def __call__(self):
        for channel in self.channels:
            self.page = 1
            self.fetch_url = self.domain.format(channel)
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
        one_piece_pattern = '<div class="image".*?>(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        url_pattern = 'href="(.*?)"'
        for item in news_list:
            url = re.findall( url_pattern, item )
            tmp = {}
            url = url[0] if url else ''
            tmp['url'] = url if url.startswith('http') else self.fetch_url + url
            tmp['text'] = []
            tmp['media_name'] = u'央视网'
            tmp = self.append_more_info( tmp )
            #print '***********************************'
            #print tmp['title']
            #print tmp['publish_ts']
            #for item in tmp['text']:
            #    print item['type'], item['data']
            #print tmp['title']
            #print '***********************************'
            self.resp.append( tmp )
            #break

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        
        url = tmp['url']
        print 'detail url is ', url
        try:
            texts = []
            image_url = url.replace('shtml','xml')
            image_url = image_url+'?randomNum='+str(time.time()/10000000000)
            print 'image url is ', image_url
            status, res = FetchData.fetch(image_url, need_status_code=True)
            if status not in ['200',200]:
                print 'get detail image is error'
                pass
            else:
                res = res.replace('\n','')
                res = res.replace("'",'"')
                title_pattern = 'title="(.*?)"'
                image_pattern = 'bigurl="(.*?)"'
                title = re.findall(title_pattern, res)
                images = re.findall( image_pattern, res )
                text_pattern = 'CDATA\[(.*?)\]'
                text = re.findall( text_pattern, res )
                res = res.replace('年','-')
                res = res.replace('月','-')
                res = res.replace('日','')
                ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2})'
                ts = re.findall( ts_pattern, res )
                for image in images:
                    _tmp = {'type':'image','data':image.strip()}
                    texts.append( _tmp )
                if text:
                    _tmp = {'type':'text','data':text[0].strip()}
                    texts.append( _tmp )
                if title:
                    tmp['title'] = title[0]
                if ts:
                    tmp['publish_ts'] = ts[0]
            tmp['text'] = texts
        except Exception, e:
            print e
        finally:
            return tmp

if __name__ =="__main__":
    #worker = CNTVWork()
    #worker()
    worker = CNTVStarImageWork()
    worker()
