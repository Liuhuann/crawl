# -*- coding:utf-8 -*-
import json
import re

def json_loads_str(str):
    """
    将字符串当作json字符串来处理 
    """
    try:
        res = json.loads(str)
        return res
    except Exception, e:
        return None
    

def html_template_to_dict(str):
    """
    将字符串当作一个html文件处理成字典，适合详情页的时候
    """
    pass

def html_template_to_list(str):
    """
    将字符串当作一个html文件处理成字典列表，适合详情页的时候
    """
    pass
