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

class MXHWork(object):
    def __init__(self, page_limit=True, total_page_count=5814, page = 1):
        self.stop_work = False
        self.fetch_url = 'http://www.591mxh.com'
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page

    def __call__(self):
        while( self.page <= self.total_page_count and not self.stop_work):
            self.fetch_page_data()
            self.page = self.page + 1

    def fetch_page_data(self):
        url = self.fetch_url + '/xing/0/' + str(self.page) + '.html'
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
        one_piece_pattern = '<div.*?class="avatar-bg">(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<h2>.*?<a title="(.*?)".*?class="post-title.*?".*?href=".*?".*?target="_blank">.*?</a>.*?</h2>'
        url_pattern = '<h2>.*?<a title=".*?".*?class="post-title.*?".*?href="(.*?)".*?target="_blank">.*?</a>.*?</h2>'
        summary_pattern = '<p.*?class="post-summarize">(.*?)</p>'
        publish_ts_pattern = '<span class="post-time">发布时间：(.*?)</span>'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            summary = re.findall( summary_pattern, item )
            publish_ts = re.findall( publish_ts_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url if url.startswith('http') else self.fetch_url + url
            tmp['summary'] = summary[0] if summary else ''
            publish_ts = publish_ts[0] if publish_ts else ''
            tmp['publish_ts'] = self.process_publish_ts( publish_ts )
            tmp['text'] = []
            tmp['media_name'] = u'明星汇'
            tmp = self.append_more_info( tmp )
            #print '***********************************'
            #print tmp['publish_ts']
            #for item in tmp['text']:
            #    print item['type'],
            #    print item['data']
            #print '***********************************'
            #break
            self.resp.append( tmp )

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        
        url = tmp['url']
        print 'detail url is ', url
        try:
            baidu = BaiduFetchAnalyst.fetch( url )
            status, res = FetchData.fetch( url, need_status_code=True ) 
            res = res.decode('utf-8')
            if status in ['200',200]:
                res = res.replace('\n','')
                res = res.replace("'",'"')
                #text_pattern = '<span.*?class="time">(.*?)class="apply-btn-box">'
                image_pattern = '<img.*?class="post-img".*?src="(.*?)".*?>'
                #text = re.findall( text_pattern, res )
                text = res
                if text:
                    #text = text[0]
                    #print 'text is ', text
                    images = re.findall(image_pattern, text)
                    print 'images length is ', len(images)
                    text = {}
                    if images:
                        for item in baidu['text']:
                            index = res.find( item['data'][:10] )
                            text[ index ] = item
                        for image in images:
                            index = res.find( image )
                            text[ index ] = { 'type':'image', 'data':image }
                        t = []
                        index = text.keys()
                        index.sort()
                        for key in index:
                            if key >= 0:
                                t.append( text[key] )
                        tmp['text']  = t   
                        print '找到图片个数为', len(images)
                    else:
                        print '没有找到图片'
                    print '找到数据'
                else:
                    print '未找到数据'
            else:
                print 'status code is not 200', url
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
    worker = MXHWork(page=800)
    worker()
