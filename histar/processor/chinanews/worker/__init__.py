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

class ChinaNewsWork(object):
    def __init__(self, page_limit=True, total_page_count=1, page = 0):
        self.stop_work = False
        self.domain = 'http://channel.chinanews.com/cns/cl/yl-mxnd.shtml'
        self.fetch_url = ''
        self.data = {}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.page = page

    def __call__(self):
        while( self.page <= self.total_page_count and not self.stop_work):
            self.fetch_page_data()
            self.page = self.page + 1

    def fetch_page_data(self):
        url = self.domain + "?pager=" + str(self.page)
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
        one_piece_pattern = '<td  class="color065590">(.*?)<td style="color:green"'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<a href=.*?>(.*?)</a>'
        url_pattern = 'href="(.*?)"'
        summary_pattern = '<font color=#818181>(.*?)</font>'
        ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            ts = re.findall( ts_pattern, item )
            summary = re.findall( summary_pattern, item )
            tmp = {}
            tmp['title'] = title[0].strip() if title else ''
            tmp['summary'] = summary[0].strip() if summary else ''
            url = url[0].strip() if url else ''
            tmp['url'] = url if url.startswith('http') else self.fetch_url + url
            tmp['publish_ts'] = ts[0] if ts else ''
            tmp['text'] = []
            tmp['media_name'] = u'中新网'
            tmp = self.append_more_info( tmp )
            print '***********************************'
            print tmp['publish_ts']
            #print tmp['title']
            #print tmp['url']
            #print tmp['summary']
            #for item in tmp['text']:
            #    print item['type'],
            #    print item['data']
            #print '***********************************'
            self.resp.append( tmp )
            break

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
            if status not in ['200',200]:
                print 'get detail page is error'
            else:
                try:
                    res = res.decode('gb2312').encode('utf-8')
                except:
                    print 'not gb2312 code'
                    res = res.decode('GBK').encode('utf-8')
                    
                res = res.replace('\n','')
                res = res.replace("'",'"')
                lindex = res.find('<!--图片start-->')
                rindex = res.find('<!--图片end-->')
                print lindex, rindex
                if lindex>=0 and rindex>=0:
                    res = res[lindex:rindex]
                    image_pattern = '<img.*?src="(.*?)".*?'
                    images = re.findall( image_pattern, res )
                    for image in images:
                        if not image.startswith('http'):
                            index = url.rfind('/')
                            image = url[:index+1]+image
                        if image not in tmp['images']:
                            tmp['images'].append(image)
                        _tmp = {'type':'image','data':image}
                        tmp['text'].insert( 0, _tmp )
        except Exception, e:
            print e
        finally:
            return tmp

if __name__ =="__main__":
    worker = ChinaNewsWork(total_page_count=1)
    tmp = {'url':'http://www.chinanews.com/yl/2015/04-24/7230894.shtml'}
    res = worker.append_more_info( tmp )
    for item in res['text']:
        print item['type']
        print item['data']
