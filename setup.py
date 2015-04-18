#-*- coding:utf-8 -*-

from setuptools import setup, find_packages
requires=[]
setup(
    name='histar',
    version='0.1',
    description='hichao star information crawl',
    packages = find_packages(),
    zip_safe=False,
    install_packages_data=True,
    install_requires=requires,
)
