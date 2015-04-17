# -*- coding:utf-8 -*-
from mongoengine import *
import datetime
from types import DictType
import hashlib

connect('chenglong',host='192.168.1.222', port=27001)

class StarInformation(DynamicDocument):
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
    text = ListField( DictField(),default={} )
    

class DBSession(object):
    @classmethod
    def save(cls,data):
        try:
            if isinstance(data, DictType):
                info = cls.fetch_star_info( data['url'] )
                for attr in data.keys():
                    setattr(info, attr, data[attr])
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
    def fetch_star_info(cls, str):
        uniq_id = cls.generate_uniq_id(str)
        print 'uniq_id is ', uniq_id
        res = StarInformation.objects(uniq_id=uniq_id).first()
        if res is None:
            print 'mongoengine find certain uniq_id is error'
            res = StarInformation()
            res.uniq_id = uniq_id
        return res

    @classmethod
    def total_count(cls):
        return StarInfomation.objects().count()
