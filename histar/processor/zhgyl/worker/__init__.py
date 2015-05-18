#-*- coding:utf-8 -*-
from histar.util.text_process import reformat_date_str
from histar.util.url_fetch import FetchData
from histar.util.baidu_fetch import BaiduFetchAnalyst
from histar.db import DBSession
import json
import re

class ZhgylWork(object):
    """
    中国娱乐网资讯抓取
    """
    def __init__(self, channel_url='http://news.yule.com.cn/{}', total_page_count=10, page=1, channel_names=['neidi','gangtai','riben','hanguo','oumei']):
        self.stop_work = False
        self.channel_url = channel_url
        self.fetch_format_url = channel_url
        self.total_page_count = total_page_count
        self.page = page
        self.channel_names = channel_names

    def __call__(self):
        for channel_name in self.channel_names:
            self.stop_work = False
            self.page = 1
            self.channel_url = self.fetch_format_url.format(channel_name)
            while( self.page <= self.total_page_count and not self.stop_work):
                self.fetch_page_data()
                self.page = self.page + 1
    def fetch_page_data(self):
        if self.page == 1:
            url = self.channel_url
        else:
            url = '%s/index%s.html' % (self.channel_url,self.page)
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
        try:
            content = content.decode('gb2312').encode('utf-8')
        except Exception,e:
            try:
                content = content.decode('gbk').encode('utf-8')
            except Exception as e:
                pass
        self.resp = []
        content = content.replace('\n','')
        content = content.replace("'",'"')

        one_piece_pattern = '<span class="mainNewsTitle">(.*?)<div class="mainListNewsHist">'
        news_list = re.findall(one_piece_pattern, content)
        print len( news_list )
        if len(news_list)==0:
            self.stop_work = True
        title_pattern = '<a href=".*?" title=".*?">(.*?)</a>'
        url_pattern = 'href="(.*?)"'
        publish_ts_pattern = '([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})'
        for item in news_list:
            title = re.findall( title_pattern, item )
            url = re.findall( url_pattern, item )
            publish_ts = re.findall( publish_ts_pattern, item )
            tmp = {}
            tmp['title'] = title[0] if title else ''
            url = url[0] if url else ''
            tmp['url'] = url 
            publish_ts = publish_ts[0] if publish_ts else ''
            tmp['publish_ts'] = reformat_date_str( publish_ts )
            tmp['text'] = []
            tmp['media_name'] = u'中国娱乐网'
            tmp = self.append_more_info( tmp )
            self.resp.append( tmp )
            # print '******************************************'
            # print tmp['publish_ts']
            # print tmp['title']
            # print tmp['url']
            # for item in tmp['text']:
            #    print item['type'],
            #    print item['data']
            # print '******************************************'
            # print tmp
            # break

    def append_more_info(self, tmp):
        """
        获取详情页的新闻正文
        """
        
        url = tmp['url']
        try:
            baidu = BaiduFetchAnalyst.fetch( url )
            tmp['text'] = baidu['text']
        except Exception, e:
            print e
        finally:
            return tmp

if __name__ =="__main__":
    worker = ZhgylWork(total_page_count=5)
    worker()

