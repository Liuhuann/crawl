#-*- coding:utf-8 -*-

import re
from histar.db import StarNews
from histar.util.url_fetch import FetchData
from histar.util.text_process import reformat_date_str

def update_publish_ts():
    offset = 0
    limit = 200
    stop = False
    while( not stop ):
        res = StarNews.objects(url__contains="www.qhtv.cn").skip(offset).limit(limit)
        offset = offset + limit
        if len( res ) == 0:
            break
        for item in res:
            publish_ts = item.publish_ts
            item.publish_ts = reformat_date_str( publish_ts )
            print item.publish_ts
            item.save()
            #if publish_ts.isdigit():
            #    print 'origin publish_ts is ', publish_ts
            #    url = item.url
            #    status_code, res = FetchData.fetch( url, need_status_code=True )
            #    if status_code in ['200<',200]:
            #        res = res.lower()
            #        index = res.find('body')
            #        print index, url
            #        if index <0 :
            #            continue
            #        res = res[index:]
            #        res = res.replace('\n','')
            #        res = res.replace('年','-')
            #        res = res.replace('月','-')
            #        res = res.replace('/','-')
            #        res = res.replace('.','-')
            #        res = res.replace('日 ','')
            #        res = res.replace('日',' ')
            #        pa = '([0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2})'
            #        ts = re.findall(pa, res)
            #        publish_ts = ''
            #        length = len( ts )
            #        if length == 1:
            #            print '找到标准的时间格式'
            #            #item.publish_ts = ts[0]
            #            #item.save()
            #            publish_ts = ts[0]
            #        elif length == 0:
            #            print '没有找到标准的时间格式'
            #        else:
            #            print '找到多余两个的时间格式'
            #            #publish_ts = ts[0]
            #        if publish_ts:
            #            if publish_ts.count('-') == 1:
            #                publish_ts = '2015-'+publish_ts
            #            item.publish_ts = publish_ts
            #            item.save()

if __name__ == '__main__':
    update_publish_ts()
