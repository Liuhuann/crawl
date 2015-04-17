#-*- coding:utf-8 -*-

from util.text_process import keep_certain_keys
from processor.sina.template_analysis import(
        json_loads_str,
        html_template_to_dict,
        html_template_to_list,
        )
from util.url_fetch import (
        FetchData,
        )
from util.baidu_fetch import (
        BaiduFetchAnalyst,
        )
from db import (
        DBSession,
        )
import urllib
import copy
import time
import json
import re

class SinaWork(object):
    def __init__(self, pageid=107, lid=1244, num=30, versionNumber='1.2.6',encode='utf-8',**kwargs):
        self.fetch_url = 'http://feed.mix.sina.com.cn/api/roll/get?'
        self.data={}
        self.data['page'] = 1
        self.data['pageid'] = pageid
        self.data['lid'] = lid
        self.data['num'] = num
        self.data['encode'] = encode
        self.data['versionNumber'] = versionNumber
        self.data['_'] = int(time.time()*1000)
        self.data.update( kwargs )

    def __call__(self):
        while( self.data['page'] <= 20 ):
            self.fetch_page_data()
            self.data['page'] = self.data['page'] + 1

    def fetch_page_data(self):
        if 'ctime' in self.data:
            del self.data['ctime']
        self.data['_'] = int(time.time()*1000)
        query = urllib.urlencode( self.data )
        url = self.fetch_url + query
        try:
            print 'first url is ', url
            self.resp = FetchData.fetch( url )
            if self.check_is_validate_requests_resp():
                self.save_data()
                self.fetch_more_data()
                #调用后续的两次请求，写入数据
            else:
                print '请求不合法'
        except Exception, e:
            pass

    def fetch_more_data(self):
        if 'ctime' in self.data:
            i= 0
            while (i < 2):
                _data = copy.deepcopy( self.data )
                del _data['page']
                _data['_'] = int(time.time()*1000)
                query = urllib.urlencode( _data )
                url = self.fetch_url + query
                i = i + 1
                try:
                    print 'more url is ', url
                    self.resp = FetchData.fetch( url )
                    if self.check_is_validate_requests_resp():
                        self.save_data()
                    else:
                        print '获取更多数据失败'
                except Exception, e:
                    print e
                    pass
            del self.data['ctime']
        else:
            print 'self data has not attr named ctime'
            
    def check_is_validate_requests_resp(self):
        """
        判断是不是一个有效的请求返回
        """
        if hasattr(self, 'resp'):
            self.resp  = json_loads_str( self.resp )
            if self.resp and self.resp['result']['status']['code'] in [0,'0']:
                print 'length is ', len(self.resp['result']['data'])
                self.data['ctime'] = self.resp['result']['end']
                self.resp = self.resp['result']['data']
                return True
            else:
                print 'self. resp status code is not 200'
                return False
        else:
            print 'self does not has attr resp'
            return False

    def save_data(self):
        if self.resp:
            for item in self.resp:
                tmp = copy.deepcopy(item)
                keep_certain_keys( tmp , ['url','wapurl','title','stitle','summary','wapsummary','intro','img','images','keywords','media_name'])
                tmp['waptitle'] = tmp['stitle']
                del tmp['stitle']
                img = [tmp['img'].get('u','')]
                images = [ image['u'] for image in tmp.get('images',[]) ]
                tmp['img'] = img
                tmp['images'] = images
                tmp = self.append_more_info( tmp )
                flag = DBSession.save( tmp )
                if not flag:
                    print 'write failed with data=', json.dumps( tmp )
                else:
                    print 'write successed '
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
            return {}
        finally:
            return tmp

    def get_detail_page_text(self,text):
        """
         获取新浪详情页的正文列表
        """
        text_pattern = '来源(.*?)发表评论'
        res = re.findall(text_pattern, text)
        if res:
            article = res[0]
            text_list = re.findall('<div.*?>(.*?)</div>', article)
            return text_list
        else:
            []


worker = SinaWork(lid=1253,pageid=108)
worker()
#worker1 = SinaWork(lid=1246)
#worker1()
#worker2 = SinaWork(lid=1247)
#worker2()
#worker3 = SinaWork(lid=1248)
#worker3()
#worker4 = SinaWork(lid=1249)
#worker4()
