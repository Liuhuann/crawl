#-*- coding:utf-8 -*-

from histar.util.text_process import(
        keep_certain_keys,
        json_loads_str,
        )
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
from datetime import datetime
import urllib
import copy
import time
import json
import re

class SinaWork(object):
    def __init__(self, total_page_count=16,pageid=107, lid=1244, num=30, versionNumber='1.2.6',encode='utf-8', page=1,**kwargs):
        self.fetch_url = 'http://feed.mix.sina.com.cn/api/roll/get?'
        self.total_page_count = total_page_count
        self.data={}
        self.stop_work = False
        self.data['page'] = page
        self.data['pageid'] = pageid
        self.data['lid'] = lid
        self.data['num'] = num
        self.data['encode'] = encode
        self.data['versionNumber'] = versionNumber
        self.data['_'] = int(time.time()*1000)
        self.data.update( kwargs )

    def __call__(self):
        while( self.data['page'] <= self.total_page_count  and not self.stop_work):
            self.fetch_page_data()
            self.data['page'] = self.data['page'] + 3

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
            if len(self.resp)==0:
                self.stop_work = True
            for item in self.resp:
                tmp = copy.deepcopy(item)
                keep_certain_keys( tmp , ['url','wapurl','title','stitle','summary','wapsummary','intro','img','images','keywords','media_name', 'ctime'])
                tmp['waptitle'] = tmp['stitle']
                del tmp['stitle']
                img = [tmp['img'].get('u','')]
                publish_ts = datetime.fromtimestamp(float(tmp['ctime'])).strftime("%Y-%m-%d %H:%M:%S")
                tmp['publish_ts'] = publish_ts
                print tmp['publish_ts']
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
            if res.get('media_name',""):
                tmp['media_name'] = res['media_name']
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                if image not in tmp['images']:
                    tmp['images'].append(image)
            text_len = len( tmp['text'] )
            if url.find('slide.ent.sina.com.cn')>=0:
                text = self.add_more_info_for_sina( url )
                if len(text) > text_len:
                    tmp['text'] = text
        except Exception, e:
            print e
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

    def add_more_info_for_sina(self,url):
        print url
        if url.find('slide.ent.sina.com.cn/') == -1:
            print 'no need more info'
            return []
        status_code , res = FetchData.fetch( url , need_status_code=True )
        if status_code not in ['200',200]:
            print 'status_code is not 200'
            return []
        else:
            try:
                res = res.replace('\n','')
                p = 'var slide_data =(.*?)var'
                l = re.findall(p, res)
                text = []
                if len(l):
                    res = l[0]
                    res = res.strip()
                    data = json.loads(res)
                    for item in data['images']:
                        tmp1 = {'type':'image','data':''}
                        tmp2 = {'type':'text','data':''}
                        if 'image_url' in item and item['image_url']:
                            tmp1['data'] = item['image_url']
                            text.append(tmp1)
                        if 'title' in item and item['title']:
                            tmp2['data'] = item['title']
                            text.append(tmp2)
                return text
            except Exception,e:
                print e
                return []
        
class SinaSlideWork(object):
    def __init__(self, total_page_count=1895,activity_size="198_132", ch_id=4, size="img", sub_ch='{in}star,star/jp,star/k,star/w,star/h',num=16,**kwargs):
        self.fetch_url = 'http://api.slide.news.sina.com.cn/interface/api_album.php?'
        self.total_page_count = total_page_count
        self.data={}
        self.data['page'] = 1
        self.data['activity_size'] = activity_size
        self.data['ch_id'] = ch_id
        self.data['num'] = num
        self.data['size'] = size
        self.data['sub_ch'] = sub_ch
        self.data['_'] = int(time.time()*1000)
        self.stop = False
        self.data.update( kwargs )

    def __call__(self):
        while( not self.stop and self.data['page'] <= self.total_page_count ):
            self.fetch_page_data()
            self.data['page'] = self.data['page'] + 1

    def fetch_page_data(self):
        self.data['_'] = int(time.time()*1000)
        query = urllib.urlencode( self.data )
        url = self.fetch_url + query
        try:
            print 'first url is ', url
            self.resp = FetchData.fetch( url )
            if self.check_is_validate_requests_resp():
                print '数据解析正确，处理数据写入数据库'
                self.save_data()
                #调用后续的两次请求，写入数据
            else:
                print '请求不合法'
        except Exception, e:
            pass

    def check_is_validate_requests_resp(self):
        """
        判断是不是一个有效的请求返回
        """
        if hasattr(self, 'resp'):
            self.resp  = json_loads_str( self.resp )
            if self.resp and self.resp['status']['code'] in [0,'0']:
                if not self.resp['data']:
                    print 'data length is 0, stop work'
                    self.stop = True
                    self.resp = []
                else:
                    print 'length is ', len(self.resp['data'])
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
            for item in self.resp:
                tmp = {}
                tmp['title'] = item['name']
                tmp['intro'] = item['short_intro']
                tmp['summary'] = item['short_name']
                tmp['url'] = item['url'].replace('/d/1', '')
                tmp['media_name'] = item['source']
                tmp['publish_ts'] = item['createtime']
                
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
            if res.get('media_name',"") and not tmp['media_name']:
                tmp['media_name'] = res['media_name']
            if 'images' not in tmp:
                tmp['images'] = []
            for image in res['images']:
                if image not in tmp['images']:
                    tmp['images'].append(image)
            text_len = len( tmp['text'] )
            if text_len <= 1:
                text = self.add_more_info_for_sina( url )
                if len(text) > text_len:
                    tmp['text'] = text
        except Exception, e:
            print e
        finally:
            return tmp

    def add_more_info_for_sina(self,url):
        print url
        if url.find('slide.ent.sina.com.cn/') == -1:
            print 'no need more info'
            return []
        status_code , res = FetchData.fetch( url , need_status_code=True )
        if status_code not in ['200',200]:
            print 'status_code is not 200'
            return []
        else:
            try:
                res = res.replace('\n','')
                p = 'var slide_data =(.*?)var'
                l = re.findall(p, res)
                text = []
                if len(l):
                    res = l[0]
                    res = res.strip()
                    data = json.loads(res)
                    for item in data['images']:
                        tmp1 = {'type':'image','data':''}
                        tmp2 = {'type':'text','data':''}
                        if 'image_url' in item and item['image_url']:
                            tmp1['data'] = item['image_url']
                            text.append(tmp1)
                        if 'title' in item and item['title']:
                            tmp2['data'] = item['title']
                            text.append(tmp2)
                return text
            except Exception,e:
                print e
                return []
        

if __name__ =="__main__":
    #worker = SinaSlideWork(total_page_count=2000)
    #worker()
    SinaWork(lid=1244,pageid=107, total_page_count=100, page=31)()
    SinaWork(lid=1245,pageid=107, total_page_count=100)()
    SinaWork(lid=1246,pageid=107, total_page_count=100)()
    SinaWork(lid=1247,pageid=107, total_page_count=100)()
    SinaWork(lid=1248,pageid=107, total_page_count=100)()
    SinaWork(lid=1249,pageid=107, total_page_count=100)()

    SinaWork(lid=54,pageid=108 , total_page_count=100)()
    SinaWork(lid=1251,pageid=108, total_page_count=100)()
    SinaWork(lid=1252,pageid=108, total_page_count=100)()
    SinaWork(lid=1253,pageid=108, total_page_count=100)()
    SinaWork(lid=1254,pageid=108, total_page_count=100)()
    SinaWork(lid=1255,pageid=108, total_page_count=100)()
