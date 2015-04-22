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
from types import DictType, ListType
import copy
import time
import json
import re

class QQWork(object):
    def __init__(self, channel_api_url='', domain='http://ent.qq.com',  page_limit=False, total_page_count=100,**kwargs):
        self.fetch_url = channel_api_url
        self.url_template = self.fetch_url+'_{0}.htm?{1}'
        self.domain = domain
        self.stop_work = False
        self.page = 1
        self.data={}
        self.page_limit = page_limit
        self.total_page_count = total_page_count
        self.data.update( kwargs )

    def __call__(self):
        while( not self.stop_work ):
            if self.page_limit and self.page > self.total_page_count : 
                break
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
        ts_pattern = '<span class="date">.*?([0-9]{2,4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*?</span'
        for item in news_list:
            img = re.findall( small_img_pattern , item )
            title = re.findall( title_pattern, item )
            intro = re.findall( intro_pattern, item )
            url = re.findall( url_pattern, item )
            media_name = re.findall( media_name_pattern, item )
            ts = re.findall( ts_pattern, item )
            tmp = {}
            tmp['img'] = img
            tmp['title'] = title[0] if title else ''
            tmp['waptitle'] = ''
            tmp['intro'] = intro[0] if intro else ''
            tmp['summary'] = tmp['intro']
            tmp['media_name'] = media_name[0] if media_name else ''
            tmp['publish_ts'] = ts[0] if ts else ''
            print tmp['publish_ts']
            url = url[0] if url else ''
            url = self.domain + url if url and url.startswith('/a') else ''
            tmp['url'] = url
            tmp = self.append_more_info( tmp )
            self.resp.append( tmp )
            break

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        url = tmp['url']
        try:
            res = BaiduFetchAnalyst.fetch( url ) 
            tmp['text'] = res['text']
            image_count = 0
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                image_count = image_count + 1
                if image not in tmp['images']:
                    tmp['images'].append(image)
            text_len = len( tmp['text'] )
            if image_count<1 and url.find('ent.qq.com')>=1:
                text = self.add_more_info_for_qq( url )
                if len(text) > text_len:
                    tmp['text'] = text
        except Exception, e:
            print e
        finally:
            return tmp

    def reset_fetch_url(self, url):
        self.page = 1
        self.stop_work = False
        self.fetch_url = url
        self.url_template = self.fetch_url+'_{0}.htm?{1}'

    def add_more_info_for_qq(self,url):
        print url
        if url.find('ent.qq') == -1:
            print 'no need more info'
            return []
        index = url.find('.htm')
        url = url[:index] + '.hdBigPic.js'
        status_code , res = FetchData.fetch( url , need_status_code=True )
        if status_code not in ['200',200]:
            print 'status_code is not 200'
            return []
        else:
            try:
                try:
                    res = res.decode('GB2312')
                except Exception, e:
                    res = res.decode('GBK')
                index = res.find('/*')
                res = res[:index]
                res = res.strip()
                res = res.replace("'",'"')
                res = json.loads( res )
                def generate_text(data, text=[]):
                    if isinstance(data,DictType):
                        if 'Name' in data.keys():
                            _type = data['Name'].lower()
                            if _type in ['bigimgurl']:
                                for item in data.get('Children',[]):
                                    tmp ={ 'type':'image','data':''}
                                    content = item.get('Content','')
                                    if content:
                                        tmp['data'] = content
                                        text.append( tmp )
                            elif _type in ['cnt_article']:
                                for item in data.get('Children',[]):
                                    tmp ={ 'type':'text','data':''}
                                    content = item.get('Content','')
                                    if content:
                                        tmp['data'] = content
                                        text.append( tmp )
                        if 'Children' in data.keys():
                            generate_text( data['Children'], text)
                    elif isinstance( data, ListType ):
                        for item in data:
                            generate_text( item, text )
                text = []
                generate_text(res, text)
                return text
            except Exception,e:
                print e
                return []
    
if __name__ == '__main__':
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
