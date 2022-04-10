# -*- coding: utf-8 -*-
# User : HJY
# Date : 2022/3/29 4:35 下午
# Name : server.py
import datetime
import json
import time

import pymysql
from flask import Flask, request
from flask_cors import cross_origin, CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
# CORS(app, resources=r'/*', supports_credentials=True)


@app.route('/')
def index():
    return "INDEX"


@app.route('/getDate', methods=['GET', 'POST'])
def get_date():
    now_date = datetime.datetime.now()
    res = list()
    for i in range(1, 15):
        d = now_date - datetime.timedelta(days=i)
        d = ''.join(str(d.date()).split('-'))
        if d == '20220402':
            continue
        res.append(d)
    return {'success': True, 'res': res}


@app.route('/getData', methods=['POST'])
def get_data():
    data = ','.join(json.loads(str(request.get_data(), encoding='utf8')))
    conn = pymysql.Connect(host='localhost', port=3306, user='root', password='root', database='demo')
    cursor = conn.cursor()
    if data:
        sql = "select location from yq where now_date in ({});".format(data)
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        res = list()
        for info in data:
            res.append(info[0].split(','))
        return {'success': True, 'res': res}
    return {'success': True, 'res': []}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090, debug=True)
    # app.run(host='0.0.0.0', port=8090, debug=True)
