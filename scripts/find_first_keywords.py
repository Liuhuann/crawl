#-*- coding:utf-8 -*-
import os
os.environ['thrift_stage'] = 'beta'
import sys
import time
import datetime
from histar.config import *
from histar.db import StarNews, StarInfo
from sqlalchemy.orm import sessionmaker
from autoload import auto_load_register_table_class

reload(sys) 
sys.setdefaultencoding('utf8')

model_mapper_configure = []
keywords_url = 'mysql+pymysql://website:GWXmYaonK4TFx1qiDGdlvWKOJ@'+MYSQL_HOST+':'+str(MYSQL_PORT)+'/search_key_words?charset=utf8mb4'
keywords_configure = {
    'mysql_url': keywords_url,
    'mapper_list':[ ('special_words','KeyWords')]
    }
model_mapper_configure.append( keywords_configure )
res = auto_load_register_table_class( model_mapper_configure )

for item in res:
    globals()[ item.__name__ ] = item

keywords_engine = KeyWords.__table__.metadata.bind
keywordssession = sessionmaker( bind = keywords_engine )

def get_all_star_name():
    session = keywordssession()
    offset = 0
    limit = 500
    data = []
    while( True ):
        res = session.query( KeyWords ).offset(offset).limit(limit).all()
        offset = offset + limit
        if len(res)==0:
            break
        for item in res:
            name = item.show_word
            if type(name).__name__ == 'unicode':
                name = name.encode('utf-8')
            name = name.strip()
            name = name.replace('-','·')
            name = name.replace('"','')
            name = name.strip()
            name = name.replace(' ','·')
            if name not in data:
                data.append( name )
    return data

def add_star_name_for_news(star_name_list):
    offset = 0
    limit = 200
    stop = False
    while( not stop and offset < 20000):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        res = list(StarNews.objects(star_name='', publish_ts__lt=now, review__in=[0,1]).order_by('-publish_ts').skip(offset).limit(limit).no_cache())
        print len(res)
        offset = offset + limit
        if 0 == len(res):
            stop = True
        for item in res:
            try:
                title = item.title
                print title , type(title).__name__
                if type(title).__name__ in['unicode']:
                    title = title.encode('utf-8')
                star_name = match_first_name( title, star_name_list )
                item.star_name = star_name
                item.review = 1
                item.save()
            except Exception, e:
                print e
                pass
            

def match_first_name(string, str_name_list):
    start_time = time.time()
    min_index = 1000
    star_name = ''
    for item in str_name_list:
        if type(item).__name__ in ['unicode']:
            item = item.encode('utf-8')
        index = string.find( item )
        if 0<= index:
            if index <= min_index:
                min_index = index
                if len(item) > len(star_name):
                    star_name = item
    end_time = time.time()
    print string , ' first_name is ', star_name, ' use time is ', end_time - start_time
    return star_name
            
        
if __name__ == '__main__':
    star_name_list = get_all_star_name()
    while( True ):
        add_star_name_for_news(star_name_list)
        time.sleep(60*3)
