#-*- coding:utf-8 -*-
from histar.util.text_process import keep_certain_keys
from histar.util.url_fetch import (
        FetchData,
        )
from histar.db import (
        StarInfo,
        )
#from util.text_process import keep_certain_keys
#from util.url_fetch import (
#        FetchData,
#        )
from histar.db import (
        StarInfo,
        DBSession,
        )
import copy
import time
import json
import re
import urllib

class SinaStarInfoFetchWork(object):
    def __init__(self, area_list = [1,2,3,4,999] ):
        self.area_list = area_list
        self.total_page = 394
        self.fetch_url = 'http://ku.ent.sina.com.cn/star/search&'
        self.page = 1
        self.data = {}

    def __call__(self):
        for area in self.area_list:
            self.data['area'] = area
            self.page = 1 
            while( self.page <= self.total_page ):
                self.fetch_one_page()
                self.page = self.page + 1 

    def fetch_one_page(self):
        self.data['page_no'] = self.page
        url = self.fetch_url + urllib.urlencode( self.data )
        print 'url is ', url
        status_code , self.resp = FetchData.fetch(url, need_status_code=True)
        if status_code in ['200',200]:
            self.process_content()
            self.save_data()
            
    def process_content(self):
        content = self.resp
        content = content.replace('\n','')
        one_piece_pattern = '<li.*?>.*?<a.*?class="item-img.*?left">(.*?)</li>'
        news_list = re.findall(one_piece_pattern, content)
        name_pattern = '<img.*?src=".*?".*?title="(.*?)".*?>'
        avatar_pattern = '<img.*?src="(.*?)".*?title=".*?".*?>'
        nation_pattern = 'nationality=.*?">.*?</a>(.*?)</p>'
        nation_id_pattern = 'nationality=(.*?)">.*?</a>.*?</p>'
        point_pattern = '<span.*?class="red">(.*?)</span>.*?</div>'
        gender_pattern = '<p><span.*?class="txt">性别:</span>(.*?)</p>'
        job_pattern = '<a.*?href=".*profession=(.*?)">'
        birthday_pattern = '<span.*?class="txt">出生日期:.*?</span>.*?([0-9]{4}.[0-9]{1,2}.[0-9]{1,2}).*?</p>'
        constellation_pattern = 'astrology=.*?">(.*?)</a></p>'
        url_pattern = '<a.*?href="(.*?)".*?title.*?">'
        height_pattern = '<p><span.*?class="txt">身高:.*?</span>(.*?)</p>'
        total_page_pattern = '<span>共(.*?)页.*?到第'
        total_page = re.findall( total_page_pattern, content )
        total_page = total_page[0] if total_page else '1000'
        print 'total page ', total_page
        if total_page.isdigit():
            self.total_page = int(total_page)
        else:
            self.total_page = 500
        self.resp = []
        if len(news_list)==0:
            self.stop_work = True
        for item in news_list:
            name = re.findall( name_pattern, item )
            avatar = re.findall( avatar_pattern, item )
            nation = re.findall( nation_pattern, item )
            nation_id = re.findall( nation_id_pattern, item )
            point = re.findall( point_pattern, item )
            gender = re.findall( gender_pattern, item )
            job = re.findall( job_pattern, item )
            birthday = re.findall( birthday_pattern, item )
            constellation = re.findall( constellation_pattern, item )
            url = re.findall( url_pattern, item )
            height = re.findall( height_pattern, item )
            tmp = {}
            tmp['name'] = name[0] if name else ''
            tmp['avatar'] = avatar[0] if avatar else ''
            tmp['nationality'] = nation[0] if nation else ''
            tmp['nationality_id'] = nation_id[0] if nation else ''
            tmp['point'] = point[0] if point else ''
            tmp['gender'] = gender[0] if gender else ''
            tmp['job'] = job
            tmp['birthday'] = birthday[0] if birthday else ''
            print tmp['birthday']
            tmp['constellation'] = constellation[0] if constellation else ''
            tmp['url'] = url[0] if url else ''
            tmp['height'] = height[0] if height else ''
            tmp['name'] = name[0] if name else ''
            self.resp.append( tmp )

    def save_data(self):
        if self.resp:
            for item in self.resp:
                flag = DBSession.save_star_info(item)
                if not flag:
                    print 'write failed with data=', json.dumps( item )
                else:
                    print 'write successed '
        else:
            print 'error with no self.resp or self.resp is not list type'

if __name__ =="__main__":
    worker = SinaStarInfoFetchWork()
    worker()
