#-*- coding:utf-8 -*-
import json
from histar.db import StarNews

def stat_al_star_and_image_count():
    offset = 0
    limit = 200
    stop = False
    star_dict = {}
    count = 0
    while ( not stop ):
        #res = StarNews.objects(review=1).skip(offset).limit(limit)
        res = list(StarNews.objects(review=1).skip(offset).limit(limit).no_cache())
        offset = offset + limit
        if len(res) == 0:
            break
        for item in res:
            text = item.text
            for t in text:
                if t['type'] == 'image' and t['data']:
                    count = count + 1
            star = item.star_name
            if star in star_dict.keys():
                star_dict[ star ] = star_dict[ star ] + 1
            else:
                star_dict[ star ] =  1
    print 'total image count is ', count
    count = 0
    for v in star_dict.itervalues():
        count = count + v
    print count
    #print json.dumps(star_dict)
    #for k, v in star_dict.iteritems():
    #    print k, v
    #return
    return star_dict

star_dict = stat_al_star_and_image_count()
with open('stat.txt','w') as hs:
    for k,v in star_dict.iteritems():
        line = k.encode('utf-8')+','+str(v)+'\n'
        hs.write(line)
