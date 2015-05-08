# -*- coding:utf-8 -*-
import hashlib
import random
import pymongo
import datetime
import requests
from file_2.sdk import *
from histar.config import *
from histar.db import StarNews
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from autoload import auto_load_register_table_class

wodfan_url = 'mysql+pymysql://website:GWXmYaonK4TFx1qiDGdlvWKOJ@'+MYSQL_HOST+':'+MYSQL_PORT+'/wodfan?charset=utf8mb4'
model_mapper_configure = []
wodfan_configure = {
    'mysql_url': wodfan_url,
    'mapper_list':[ ('histar_images','HIImage')]
    }
model_mapper_configure.append( wodfan_configure )

keywords_url = 'mysql+pymysql://website:GWXmYaonK4TFx1qiDGdlvWKOJ@'+MYSQL_HOST+':'+MYSQL_PORT+'/search_key_words?charset=utf8mb4'
keywords_configure = {
    'mysql_url': keywords_url,
    'mapper_list':[ ('special_words','KeyWords')]
    }
model_mapper_configure.append( keywords_configure )
res = auto_load_register_table_class( model_mapper_configure )

for item in res:
    globals()[ item.__name__ ] = item

wodfan_engine = create_engine( wodfan_url, pool_recycle=30 )
keywords_engine = create_engine( keywords_url, pool_recycle=30 )
wodfansession = sessionmaker( bind = wodfan_engine )
keywordssession = sessionmaker( bind = keywords_engine )

ns = 'test_download'

def get_all_proxies():
    client = pymongo.MongoClient("192.168.1.110", 30001)
    table = client['spiders_manage']['proxy']
    data = table.distinct('ip')
    return data

all_proies = get_all_proxies()

def load_all_star_name():
    data = {}
    stop = False
    offset = 0
    limit = 200
    session = keywordssession()
    while( not stop):
        res = session.query(KeyWords).filter_by(category='明星').offset(offset).limit(limit).all()
        offset = offset + limit
        if len(res)==0:
            stop = True
        for item in res:
            id = item.id
            name = item.show_word
            data[ id ] = name
    session.close()
    return data
    return data

def generate_filename( content, ext):
    md5 = hashlib.md5()
    md5.update(content)
    return str(md5.hexdigest()) + '.' + ext

def down_img_from_url(url, referer):
    try:
        headers = {}
        headers['Referer'] = referer
        headers["User-Agent"] = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; MyIE9; BTRS123646; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)"
        headers["Accept"] = "*/*"

        index = random.randint(0, len(all_proies)-1)
        proxy = all_proies[index]
        print proxy
        proxies = {'http':proxy}
        
        #resp = requests.get( url, timeout=60, headers=headers, proxies=proxies )
        resp = requests.get( url, timeout=60, headers=headers )
        if resp.status_code not in ['200',200]:
            return None
        else:
            return resp.content
    except Exception, e:
        print e
        return None

def download_image(origin_image_list, referer):
    """
      下载图片列表.
    """
    data = {}
    flag = True
    for url in origin_image_list:
        if not url.startswith('http'):
            continue
        print 'url is ', url
        res = down_img_from_url(url, referer)
        if res is None:
            flag = False
            print '下载出错'
        else:
            ext = get_url_extname(url)
            filename = generate_filename( res, ext )
            code = add_file_2( ns, filename, ext, res, '')
            if code:
                data[ url ] = filename
            else:
                print code
                print '保存图片出错'
                flag = False

    return flag, data

def update_star_news_with_download_image():
    """
      下载mongo中的明星资讯，处理每条资讯的图片下载任务.
    """
    star_name_dict = load_all_star_name()
    offset = 0
    limit = 10
    stop = False
    while( not stop ):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        res = StarNews.objects(download_img=0, publish_ts__lt=now).order_by('-publish_ts').skip(offset).limit(limit)
        offset = offset + limit
        if len(res)==0:
            stop = True
        def get_star_news_images(obj):
            data = []
            for item in obj.text:
                if item['type'] == 'image' and item['data'] not in data:
                    data.append( item['data'] )
            return data

        def update_star_news_text_images(obj, data):
            for item in obj.text:
                if item['type'] in ['image']:
                    if item['data'] in data.keys():
                        url = item['data']
                        item['data'] = data[ url]
                    else:
                        print item['data']
                        print '明星资讯图片下载失败'
        for obj in res:
            print 'page url is', obj.url
            _images = get_star_news_images( obj )
            downloaded_image_dict = get_downloaded_images_dict( _images )
            images = [ image for image in _images if image not in downloaded_image_dict.keys() ]
            if images:
                flag, image_dict = download_image( images, obj.url )
                star_id, star_name = match_first_name( obj.title, star_name_dict )
                #将新增的下载的图片保存起来
                save_downloaded_images( star_id, image_dict )
                #将已经下载保存过的图片更新，用于更新mongo的资讯
                image_dict.update( downloaded_image_dict )
                #update_star_news_text_images( obj, image_dict )
                if flag:
                    print '图片下载成功'
                    obj.download_img = 1
                    obj.star_name = star_name
                    obj.save()
            else:
                print '没有图片'
                obj.download_img = 1
                obj.save()
        break
                    
def match_first_name(string, star_name_dict):
    """
      找到文本中出现的第一个明星的名字和star_id返回.
    """
    min_index = 1000
    star_id = 0
    star_name = ''
    if type(string).__name__ in ['unicode']:
        string = string.encode('utf-8')
    for id, item in star_name_dict.iteritems():
        if type(item).__name__ in ['unicode']:
            item = item.encode('utf-8')
        index = string.find( item )
        if 0<= index:
            if index <= min_index:
                min_index = index
                star_id = id
                if len(item) > len(star_name):
                    star_id = id
    return star_id, star_name

def save_downloaded_images(star_id, image_dict):
    """
      将下载的图片保存起来.
    """
    obj_list = []
    for origin, filename in image_dict.iteritems():
        obj = HIImage()
        obj.original_url = origin
        obj.review = -1
        obj.star_id = int(star_id)
        obj.image = filename
        obj_list.append( obj )
        
    if obj_list:
        try:
            session = wodfansession()
            session.add_all(obj_list)
            session.flush()
            session.commit()
            session.close()
            print '新增图片保存成功'
        except Exception, e:
            print e
    return

def get_downloaded_images_dict(image_list):
    """
      获取已经下载过的图片的信息.
    """
    session = wodfansession()
    res = session.query( HIImage ).filter( HIImage.original_url.in_(image_list) ).all()
    data = {}
    for item in res:
        data[ item.original_url ] = item.image
    session.close()
    return data

if __name__ == '__main__':
    update_star_news_with_download_image()
    print 'all done'
