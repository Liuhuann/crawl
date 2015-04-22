#-*- coding:utf-8 -*-
from histar.util.text_process import keep_certain_keys
from histar.util.url_fetch import (
        FetchData,
        )
from histar.util.text_process import (
        reformat_date_str,
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

class QHTVWork(object):
    def __init__(self, total_page_count=155):
        self.stop_work = False
        self.total_page_count = total_page_count
        self.fetch_url = 'http://www.qhtv.cn/ent/'
        self.page = 1
        

    def __call__(self):
        while( not self.stop_work ):
            self.fetch_page_data()
            self.page = self.page + 1
            if self.page >= self.total_page_count:
                self.stop_work = True
    
    def fetch_page_data(self):
        url = self.fetch_url + '?page=' + str(self.page)
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
        content = self.resp.decode('GBK').encode('utf-8')
        self.resp = []
        content = content.replace("'",'"')
        content = content.replace("\n",'')
        one_piece_pattern = '<dl class="bbda cl">(.*?)</dl>'
        news_list = re.findall(one_piece_pattern, content, re.MULTILINE)
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<h1>(.*?)</h1>'
        url_pattern = '<dt.*?class="xs2">.*?<a.*?href="(.*?)"'
        ts_pattern = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2})'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            ts = re.findall( ts_pattern, item)
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url
            tmp['publish_ts'] = ts[0] if ts else ''
            tmp['media_name'] = '青海卫视'
            tmp['publish_ts'] = reformat_date_str( tmp['publish_ts'] )
            print tmp['publish_ts']
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
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                if image not in tmp['images']:
                    tmp['images'].append(image)
        except Exception, e:
            print e
        finally:
            return tmp

    def process_publish_ts(self, ts):
        l = re.split('-|:| ', ts)
        ts = l[0]
        for item in l:
            if len(item) == 1:
                item = '0'+item
        for item in l[1:3]:
            ts = ts + '-' + item
        ts = ts + l[3] if len(l)>=3 else ts
        for item in l[4:]:
            ts = ts + ':' + item
        print ts
        return ts

if __name__ =="__main__":
    worker = QHTVWork( total_page_count=151)
    worker()
