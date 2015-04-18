# -*- coding:utf-8 -*-
import json
import re

def convert_to_list(str):
    try:
        res = json.loads(str)
        res = res.get('result',{})
        status = res.get('status',None)
        if status and status['code']==0:
            data = []
            for item in res['data']:
                data.append()
        else:
            #此处应该加上日志
            return []
    except Exception, e:
        return []
    

def html_template_to_dict(str):
    pass

def html_template_to_list(str):
    pass
