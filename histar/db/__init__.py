# -*- coding:utf-8 -*-
from mongoengine import *
from histar.config import *
import datetime
from types import DictType
import hashlib
from histar.util.text_process import html_tags_parser

connect('histar',host=MONGO_HOST, port=MONGO_PORT)

class StarNews(DynamicDocument):
    keywords = StringField(default='')
    intro = StringField(default='')
    uniq_id = StringField(default='')
    img = ListField(StringField(),default=[])
    images = ListField(StringField(),default=[])
    media_name = StringField(default='')
    update_ts = DateTimeField(default=datetime.datetime.now)
    publish_ts = StringField(default='')
    summary = StringField(default='')
    wapsummary = StringField(default='')
    url = StringField(default='')
    wapurl = StringField(default='')
    title = StringField(default='')
    waptitle = StringField(default='')
    text = ListField( DictField(),default=[] )
    review = IntField( default=0 )
    star_name = StringField( default='' )
    download_img = IntField( default=0 )
    
class StarInfo(DynamicDocument):
    name = StringField(default='')
    gender = StringField(default='')
    job = ListField(StringField(),default=[])
    avatar = StringField(default='')
    nationality= StringField(default='')
    nationality_id = StringField(default='')
    birthday = StringField(default='')
    height = StringField(default='')
    constellation = StringField(default='')
    point = StringField(default='')
    review = IntField( default=0 )
    url = StringField( default='' )

class DBSession(object):
    need_update = False
    @classmethod
    def save(cls,data):
        try:
            if isinstance(data, DictType):
                exists,info = cls.fetch_star_info( data['url'] )
                if exists and not cls.need_update:
                    print '存在已经抓取的，不需要更新'
                    return True
                for attr in data.keys():
                    if isinstance(data[attr], list):
                        for l in data[attr]:
                            for k in l.keys():
                                l[k] = html_tags_parser( l[k] )
                        setattr(info,attr,data[attr])
                        
                    else:
                        value = html_tags_parser( data[attr] )
                        setattr(info, attr, value)
                info.save()
                return True
            else:
                return False
        except Exception,e:
            print e
            return False

    @classmethod
    def generate_uniq_id(cls, _str):
        try:
            if type(_str).__name__ in ['unicode']:

                _str = _str.encode('utf-8')
            md5 = hashlib.md5()
            md5.update(_str)
            res = md5.hexdigest()
        except Exception, e:
            print 'Generate uniq id is error with ', e
            res = ''
        finally:
            return res

    @classmethod
    def fetch_star_info(cls, _str):
        uniq_id = cls.generate_uniq_id(_str)
        print 'uniq_id is ', uniq_id
        res = StarNews.objects(uniq_id=uniq_id).first()
        if res is None:
            print 'mongoengine find certain uniq_id is error'
            res = StarNews()
            res.uniq_id = uniq_id
            return False, res
        else:
            print _str
            return True, res

    @classmethod
    def total_count(cls):
        return StarInfomation.objects().count()

    @classmethod
    def save_star_info(cls,data):
        try:
            avatar = data['avatar']
            res = StarInfo.objects(avatar=avatar).first()
            if res:
                return True
            res = StarInfo()
            for attr in data.keys():
                setattr(res, attr, data[attr])
            res.save()
            return True
        except Exception, e:
            print e
            return False

