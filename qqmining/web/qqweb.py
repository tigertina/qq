# -*- coding:utf-8 -*-

import json
import logging
import datetime
import os
import pickle
import random
from configparser import ConfigParser
import dpkt
from elasticsearch import Elasticsearch

from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory
from qqlib.utils.qq_constants import QQConstants
from qqlib.utils.qq import QQ

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'pcap', 'doc', 'docx'])
es = Elasticsearch([{'host': '219.245.186.69', 'port': 9200}])

NODE_INDEX = 'neo4j-index-node'
RELATIONSHIP_INDEX = 'neo4j-index-relationship'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='qq_monitor.log',
                    filemode='w')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    file_extension = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and file_extension in ALLOWED_EXTENSIONS


@app.route('/network', methods=['GET', 'POST'])
def network():
    if request.method == 'GET':
        return render_template('network.html', tag_result=None, social_result=None)
    else:
        file = request.files['network-file']
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        tag_result = list()
        tag_result.append(['http://www.baidu.com', u'搜索'])
        tag_result.append(['http://www.sina.com', u'娱乐'])
        social_result = list()
        social_result.append(['百度', 'qingyuanxingsi@163.com'])
        social_result.append(['微信', 'qingyuanxingsi'])
        return render_template('network.html', tag_result=tag_result, social_result=social_result)


@app.route('/qq', methods=['POST'])
def qq():
    qq_num = request.values.get('qq_num', '')
    conf = ConfigParser()
    conf.read('qqweb.config')
    qq_uin = str(conf.get('qq_config', 'qq_uin')).strip()
    qq_pwd = str(conf.get('qq_config', 'qq_pwd')).strip()
    state_dict = {0: u'正常',
                  1: u'爬取QQ号登录需要验证码，请更换登录QQ号！',
                  2: u'爬取QQ号被冻结，请更换登录QQ号!',
                  3: u'爬取QQ号登录失败，请更换登录QQ号!',
                  4: u'主动退出'}
    qq_helper = QQ(qq_uin, qq_pwd, max_page=5, nohup=True, wait=False)
    """
    print('Monitoring login...')
    qq_helper.monitor_login()
    print(qq_helper.login_tag)
    """
    # qq_helper.login_tag = random.randint(0, 3)
    qq_helper.login_tag = 0
    if qq_helper.login_tag == 0:
        # tag, profile = qq_helper.profile(qq_num)
        tag = 0
        user_profile = {"uin": 1341801774,
                        "is_famous": 0,
                        "famous_custom_homepage": 0,
                        "nickname": "浮 華 一 玍",
                        "emoji": [],
                        "spacename": "浮 華 一 玍的空间",
                        "desc": "",
                        "signature": "",
                        "avatar": "http://b123.photo.store.qq.com/psb?/V115MMLI42hzHw/3rL4Z1WdZwEt17l0vF.lSQpf9Uyd3wsGoTGAqrXsq.o!/b/dDqHVkmFDgAA&amp;bo=kADiAAAAAAABAFU!",
                        "sex_type": 0,
                        "sex": 2,
                        "animalsign_type": 0,
                        "constellation_type": 0,
                        "constellation": 9,
                        "age_type": 0,
                        "age": 24,
                        "islunar": 0,
                        "birthday_type": 0,
                        "birthyear": 1993,
                        "birthday": "01-14",
                        "bloodtype": 0,
                        "address_type": 0,
                        "country": "中国",
                        "province": "陕西",
                        "city": "西安",
                        "home_type": 0,
                        "hco": "",
                        "hp": "",
                        "hc": "",
                        "marriage": 1,
                        "career": "",
                        "company": "",
                        "cco": "",
                        "cp": "",
                        "cc": "",
                        "cb": "",
                        "mailname": "",
                        "mailcellphone": "",
                        "mailaddr": "",
                        "qzworkexp": [],
                        "qzeduexp": [],
                        "ptimestamp": 1483580293}
        profile = json.dumps(user_profile)
        friends = set()
        friends.add('302713508')
        friends.add('1531474354')
        """
        if tag == 0:
            result, friends = qq_helper.friends(qq_num)
            print(friends)
        """
        result = {'state': 0,
                  'tip': '',
                  'profile': profile,
                  'friends': ','.join(list(friends))}
    else:
        result = {'state': qq_helper.login_tag,
                  'tip': state_dict[qq_helper.login_tag]}
    return json.dumps(result)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html', user_result=None)
    else:
        result = es.search(index=NODE_INDEX, doc_type='QQ')
        total = result['hits']['total']
        hits = result['hits']['hits']

        final_user_result = []
        user_ids = []
        for hit in hits:
            source = hit['_source']
            doc_id = hit['_id']
            if 'name' not in source:
                source['name'] = ''
            name = source['name']
            uin = source['uin']
            final_user_result.append((doc_id, uin, name))
        return render_template('search.html', user_result=final_user_result)


@app.route('/password')
def password():
    return render_template('password.html')


@app.route('/crawl')
def crawl():
    return render_template('crawl.html')


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, host='0.0.0.0', port=8081)
