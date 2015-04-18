#-*- coding:utf-8 -*-
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
