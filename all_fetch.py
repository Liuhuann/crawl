# -* -coding:utf-8 -*-

from multiprocessing import Process
from histar.processor.baidu.worker import BaiduWork
from histar.processor.sina.worker import SinaWork
from histar.processor.qq.worker import QQWork
from histar.processor.xinhua.worker import XinhuaWork
from histar.processor.toutiao.worker import ToutiaoWork

if __name__ == '__main__':
    worker_list = []
    worker_list.append( ToutiaoWork() ) #今日头条
    worker_list.append( XinhuaWork(past_news_need=True, total_page_count=200, page_limit=True) ) #今日头条
    worker_list.append( QQWork('http://ent.qq.com/c/wbbl') )
    worker_list.append( QQWork('http://ent.qq.com/c/mxzx') )
    worker_list.append( QQWork('http://ent.qq.com/c/dlxw') )
    worker_list.append( QQWork('http://ent.qq.com/c/omxwn') )
    worker_list.append( QQWork('http://ent.qq.com/c/txdj') )
    
    worker_list.append( SinaWork(lid=1244,pageid=107, total_page_count=200) )
    worker_list.append( SinaWork(lid=1245,pageid=107, total_page_count=200) )
    worker_list.append( SinaWork(lid=1246,pageid=107, total_page_count=200) )
    worker_list.append( SinaWork(lid=1247,pageid=107, total_page_count=200) )
    worker_list.append( SinaWork(lid=1248,pageid=107, total_page_count=200) )
    worker_list.append( SinaWork(lid=1249,pageid=107, total_page_count=200) )
    
    worker_list.append( SinaWork(lid=54,pageid=108 , total_page_count=200) )
    worker_list.append( SinaWork(lid=1251,pageid=108, total_page_count=200) )
    worker_list.append( SinaWork(lid=1252,pageid=108, total_page_count=200) )
    worker_list.append( SinaWork(lid=1253,pageid=108, total_page_count=200) )
    worker_list.append( SinaWork(lid=1254,pageid=108, total_page_count=200) )
    worker_list.append( SinaWork(lid=1255,pageid=108, total_page_count=200) )
    
    worker_list.append( BaiduWork(cmd=4, channel_name='star' ) )
    worker_list.append( BaiduWork(cmd=4, channel_name='star_chuanwen' ) )
    worker_list.append( BaiduWork(cmd=4, channel_name='star_gangtai' ) )
    worker_list.append( BaiduWork(cmd=4, channel_name='star_neidi' ) )
    worker_list.append( BaiduWork(cmd=4, channel_name='star_oumei' ) )
    worker_list.append( BaiduWork(cmd=4, channel_name='star_rihan' ) )
    for worker in worker_list:
        p = Process(target=worker)
        p.start()
        p.join()
        print 'all is done'
