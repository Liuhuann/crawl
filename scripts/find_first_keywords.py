#-*- coding:utf-8 -*-

import time
from histar.db import StarNews, StarInfo

def get_all_star_name():
    res = StarInfo.objects().all()
    data = []
    for item in res:
        data.append( item.name.strip() )
    return data

def update_histar_info():
    offset = 0
    limit = 200
    stop = False
    while( not stop ):
        res = StarInfo.objects().skip(offset).limit(limit) 
        print offset
        for item in res:
            name = item.name
            print name, type(name).__name__
            if type(name).__name__ in ['unicode']:
                name = name.encode('utf-8')
            name = name.strip()
            name = name.replace('-','·')
            name = name.replace('"','')
            name = name.strip()
            name = name.replace(' ','·')
            item.name = name
            #res.name = name.encode('utf-8')
            item.save()
        offset = offset + limit

def add_star_name_for_news():
    star_name_list = get_all_star_name()
    offset = 0
    limit = 200
    stop = False
    while( not stop ):
        res = list(StarNews.objects(star_name='', review=0).order_by('-publish_ts').skip(offset).limit(limit).no_cache())
        print len(res)
        offset = offset + limit
        if 0 == len(res):
            stop = True
        for item in res:
            try:
                star_name = match_first_name( item.title, star_name_list )
                item.star_name = star_name
            except Exception, e:
                pass
            item.review = 1
            item.save()
            

def match_first_name(string, str_name_list):
    start_time = time.time()
    min_index = 1000
    star_name = ''
    for item in str_name_list:
        index = string.find( item )
        if 0<= index:
            if index <= min_index:
                min_index = index
                if len(item) > len(star_name):
                    star_name = item
            #if index < 1:
            #    star_name = item
            #    break
            #else:
            #    if index < min_index:
            #        min_index = index
            #        star_name = item
    end_time = time.time()
    print string , ' first_name is ', star_name, ' use time is ', end_time - start_time
    return star_name
            
        
if __name__ == '__main__':
    add_star_name_for_news()
