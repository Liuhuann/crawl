#-*- coding:utf-8 -*-
import re
import json
from types import ListType, DictType

def keep_certain_keys(data, key_list):
    """
    保留data中的某些属性
    """
    if isinstance( data, ListType ):
        for item in data:
            keep_certain_keys( item, ListType )
    elif isinstance( data, DictType ):
        delete_keys = [ key for key in data.keys() if key not in key_list ]
        for key in delete_keys:
            del data[key]
                                    
def json_loads_str(str):
    """
    将字符串当作json字符串来处理 
    """
    try:
        res = json.loads(str)
        return res
    except Exception, e:
        return None

def reformat_date_str(ts):
    l = re.split('-|:| ', ts)
    _l = []
    for item in l:
        if len(item)==1:
            item = '0'+item
        _l.append(item)
    ts = _l[0]
    for item in _l[1:3]:
        ts = ts+'-'+item
    ts = ts+' '+_l[3] if len(_l)>3 else ts
    for item in _l[4:]:
        ts = ts+':'+item
    return ts

if __name__ == '__main__':
    print reformat_date_str('2015-2-1')
    print reformat_date_str('2015-02-1')
    print reformat_date_str('2015-2-01')
    print reformat_date_str('2015-02-01 9:10')
    print reformat_date_str('2015-02-01 9:1')
    print reformat_date_str('2015-02-01 9:1:1')
