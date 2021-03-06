#-*- coding:utf-8 -*-
import re
import json
from types import DictType, ListType
from histar.db import StarNews
from histar.util.url_fetch import FetchData


def fill_more_data_for_empty():
    offset = 0
    limit = 200
    stop = False
    size = 0
    while ( not stop ):
        #res = StarNews.objects(url__contains="slide.ent.sina.com.cn", text__size=size, review__lt=2).skip(offset).limit(limit)
        #res = StarNews.objects(url__contains="ent.qq", text__size=size, review__lt=2).skip(offset).limit(limit)
        res = StarNews.objects(url__contains="toutiao.com", review__lt=2).skip(offset).limit(limit)
        offset = offset + limit 
        if len(res)==0:
            break
        for item in res:
            print 'item review ', item.review
            url = item.url
            #if url.find('slide.ent.sina.com.cn/')>=0:
            #    print 'sina'
            #    add_more_info_for_sina(item)
            #elif url.find('ent.qq.com/')>=0:
            #    print 'qq'
            #    add_more_info_for_qq(item)
            if url.find('toutiao')>=0:
                print 'toutiao'
                add_more_info_for_toutiao( item )
    return

def add_more_info_for_qq(obj):
    url = obj.url
    index = url.find('.htm')
    url = url[:index] + '.hdBigPic.js'
    status_code , res = FetchData.fetch( url , need_status_code=True )
    if status_code not in ['200',200]:
        print 'status_code is not 200'
        return
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
            if text and len(text) > len(obj.text):
                obj.text = text
                if obj.review > 1:
                    obj.review = 1
                obj.save()
            print len(text)
        except Exception,e:
            print e

def add_more_info_for_sina(obj=None):
    url = obj.url
    print url
    status_code , res = FetchData.fetch( url , need_status_code=True )
    if status_code not in ['200',200]:
        print 'status_code is not 200'
        return
    else:
        try:
            res = res.replace('\n','')
            print res.find('var slide_data =')
            p = 'var slide_data =(.*?)var'
            l = re.findall(p, res)
            print obj.uniq_id
            if len(l):
                res = l[0]
                res = res.strip()
                data = json.loads(res)
                text = []
                for item in data['images']:
                    tmp1 = {'type':'image','data':''}
                    tmp2 = {'type':'text','data':''}
                    if 'image_url' in item and item['image_url']:
                        tmp1['data'] = item['image_url']
                        text.append(tmp1)
                    if 'title' in item and item['title']:
                        tmp2['data'] = item['title']
                        text.append(tmp2)
                if text and len(text) > len(obj.text):
                    obj.text = text
                    if obj.review > 1:
                        obj.review =  1
                    obj.save()
        except Exception,e:
            print e
    
def add_more_info_for_toutiao(obj=None):
    url = obj.url
    print url
    status_code , res = FetchData.fetch( url , need_status_code=True )
    if status_code not in ['200',200]:
        print 'status_code is not 200'
        return
    else:
        try:
            res = res.decode('utf-8')
            res = res.replace('\n','')
            res = res.replace("'",'"')
            lindex = res.find('article-content')
            rindex = res.find('comments-anchor')
            if lindex>= 0 and rindex>0:
                res = res[lindex:rindex]
            p = '<img .*?src="(.*?)"'
            images = re.findall(p, res)
            text = {}
            if images:
                for item in obj['text']:
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
                obj['text']  = t   
                obj.save()
                print '找到图片个数为', len(images)
            else:
                print '没有找到图片'
        except Exception,e:
            print e
    
    

fill_more_data_for_empty()
