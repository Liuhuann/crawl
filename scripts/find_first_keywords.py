#-*- coding:utf-8 -*-

import time
from histar.db import StarNews, StarInfo

def get_all_star_name():
    res = StarInfo.objects().all()
    data = []
    for item in res:
        data.append( item.name )
    return data

def add_star_name_for_news():
    star_name_list = get_all_star_name()
    offset = 0
    limit = 200
    stop = False
    while( not stop ):
        res = StarNews.objects(review=0).order_by('-publish_ts').skip(offset).limit(limit)
        print len(res)
        offset = offset + limit
        if 0 == len(res):
            stop = True
        for item in res:
            star_name = match_first_name( item.title, star_name_list )
            item.review = 1
            item.star_name = star_name
            item.save()
            

def match_first_name(string, str_name_list):
    start_time = time.time()
    min_index = 1000
    star_name = ''
    for item in str_name_list:
        index = string.find( item )
        if 0<= index:
            if index < 2:
                star_name = item
            else:
                if index < min_index:
                    min_index = index
                    star_name = item
    end_time = time.time()
    print string , ' first_name is ', star_name, ' use time is ', end_time - start_time
    return star_name
            
        
if __name__ == '__main__':
    add_star_name_for_news()
