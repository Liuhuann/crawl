# -*-coding:utf-8 -*-

import logging

logger = logging.Logger('baidu.fetch.failed.url')
handler = logging.FileHandler('baidu.fetch.failed.url.txt')
handler.setLevel( logging.DEBUG )
logger.addHandler( handler )
