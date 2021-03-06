# -*- coding:utf-8 -*-

from setuptools import setup

packages = [
    'qqlib',
    'qqlib.entities',
    'qqlib.utils'
]

setup(
    name='qqhelper',
    version='0.9.0',
    description='A Simple QQ Zone Crawler.',
    author='qingyuanxingsi',
    author_email='qingyuanxingsi@163.com',
    packages=packages,
    package_dir={'qqlib': 'qqlib'},
    license='Apache 2.0',
    zip_safe=False
)
