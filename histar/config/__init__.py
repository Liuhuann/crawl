#-*- coding:utf-8 -*-

import os

thrift_stage = os.environ.get('thrift_stage','beta')
if thrift_stage=='beta':
    MONGO_HOST = '192.168.1.222'
    MONGO_PORT = 27001
    MYSQL_HOST = '192.168.1.20'
    MYSQL_PORT = '3306'
elif thrift_stage=='yanjiao':
    MONGO_HOST = '192.168.1.82'
    MONGO_PORT = 30001
    MYSQL_HOST = '192.168.1.108'
    MYSQL_PORT = '3307'
