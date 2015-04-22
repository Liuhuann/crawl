#-*- coding:utf-8 -*-
from histar.util.text_process import keep_certain_keys
from histar.util.url_fetch import (
        FetchData,
        )
from histar.util.baidu_fetch import (
        BaiduFetchAnalyst,
        )
from histar.util.text_process import (
        reformat_date_str,
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

class PeopleWork(object):
    def __init__(self, page_limit=True, total_page_count=4, page = 1):
        self.stop_work = False
        self.fetch_url = 'http://ent.people.com.cn/GB/1082/index{0}.html'
        self.domain = 'http://ent.people.com.cn'
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
        try:
            content = self.resp.decode('gb2312').encode('utf-8')
        except:
            content = self.resp.decode('GBK').encode('utf-8')
        self.resp = []
        content = content.replace('\n','')
        content = content.replace("'",'"')
        content = content.replace('年','-')
        content = content.replace('月','-')
        content = content.replace('日',' ')
        index = content.find('下一页')
        if index>=0:
            content = content[index:]
        else:
            return
        one_piece_pattern = '<li>(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<a.*?>(.*?)</a>'
        url_pattern = 'href="(.*?)"'
        publish_ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2})'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            publish_ts = re.findall( publish_ts_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url if url.startswith('http') else self.domain + url
            publish_ts = publish_ts[0] if publish_ts else ''
            tmp['publish_ts'] = reformat_date_str( publish_ts )
            tmp['text'] = []
            tmp['media_name'] = u'人民网'
            tmp = self.append_more_info( tmp )
            print '***********************************'
            print tmp['publish_ts']
            print '***********************************'
            self.resp.append( tmp )

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        
        url = tmp['url']
        print 'detail url is ', url
        try:
            res = BaiduFetchAnalyst.fetch( url ) 
            tmp['text'] = res['text']
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                if image not in tmp['images']:
                    tmp['images'].append(image)
            text_len = len( tmp['text'] )
            if text_len <= 1:
                text = self.add_more_info_for_qq( url )
                if len(text) > text_len:
                    tmp['text'] = text
        except Exception, e:
            print e
        finally:
            return tmp

if __name__ =="__main__":
    worker = PeopleWork()
    worker()
