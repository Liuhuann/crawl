# -*- coding:utf-8 -*-
from histar.util.url_fetch import (
        FetchData,
        )
from histar.util.text_process import (
        json_loads_str,
        )
from histar.log import (
        logger,
        )
import copy
import urllib

class BaiduFetchAnalyst(object):
    url = 'http://m.baidu.com/news?'
    data = {'tn':'bdapitext'}
    @classmethod
    def fetch(cls,fetch_url):
        _data = copy.deepcopy( cls.data )
        _data['src'] = fetch_url
        _url = cls.url + urllib.urlencode( _data )
        content = FetchData.fetch(_url)
        return cls.content_process( content )

    @classmethod
    def content_process(cls, content):
        res = {'publish_ts':"",'images':[],'text':[],'media_name':''}
        if content is None:
            return res
        else:
            data = json_loads_str( content )
            if not data.get('time','') or not data.get('title','') or not data.get('author',''):
                return res
            res['publish_ts'] = data.get('time','')
            res['title'] = data.get('title','')
            res['media_name'] = data.get('author','')
            content = data.get('content',[])
            images = []
            text = []
            for item in content:
                content_type = item.get('type','')
                tmp = {'type':content_type}
                if content_type in ['image']:
                    data = item.get('data',{})
                    images.append( data.get('original','') )
                    tmp['data'] = data.get('original','')
                    text.append( tmp )
                elif content_type in ['text']:
                    tmp['data'] = item.get('data','')
                    text.append( tmp )
            res['images'] = images
            res['text'] = text
            return res
