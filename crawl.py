"""
爬取数据
"""
import requests
import json
import time
import random
import datetime
import collections
import hjson

from satelliteData import SatelliteData


def get_cookie(username, password):
    url = 'http://www.ygzx.cast/db/login/login.edq'
    data = {
        'loginid': username,  # name
        'password': password  # password
    }
    headers = {
        'Referer': 'http://www.ygzx.cast/db/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.43 Safari/537.36'
    }
    r = requests.get(url=url, headers=headers, params=data)
    if r.status_code == 200:
        cookies = requests.utils.dict_from_cookiejar(r.cookies)
        cookie = "JSESSIONID=" + cookies['JSESSIONID']
        return cookie
    s = requests.session()
    s.keep_alive = False
    return None


def crawl_menu(cookie, date_stamp):
    menu_url = 'http://www.ygzx.cast/db/satsubalone/findgrantusergroupequipmenttree.edq'
    menu_headers = {
        'Cookie': cookie,
        'Host': 'www.ygzx.cast',
        'Referer': 'http://www.ygzx.cast/db/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.43 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    menu_data = {
        '_dc': date_stamp,
        'sys_resource_id': '-1',
    }
    r = requests.get(url=menu_url, headers=menu_headers, params=menu_data)
    # with open('ment.json', 'w', encoding='utf-8') as f:
    #     f.write(r.text.replace("nodes", '"nodes"'))
    # print('写入ment.json成功')
    modellist = []
    items = json.loads(r.text.replace("nodes", '"nodes"'))
    s = requests.session()
    s.keep_alive = False
    return items['nodes']


def find_grant(date_stamp, cookie, sat_id, telemetry_name):
    menu_headers = {
        'Cookie': cookie,
        'Host': 'www.ygzx.cast',
        'Referer': 'http://www.ygzx.cast/db/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.43 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    # key
    search_data = {
        '_dc': int(date_stamp),
        'sat_id': sat_id,
        'id': sat_id,
        'key': telemetry_name,
        'page': '1',
        'start': '0',
        'limit': '50',
    }
    search_url = 'http://www.ygzx.cast/db/tmparams/findgrantusergrouptmparamquerypage.edq'
    r = requests.get(url=search_url, headers=menu_headers, params=search_data)
    # with open('search.json', 'w', encoding='utf-8') as ff:
    #     ff.write(r.text)
    # print('写入search.json成功')
    numlist = []
    items = r.json()
    s = requests.session()
    s.keep_alive = False
    return items['records']


def crawldata(date_stamp, cookie, mid, telemetry_id, telemetry_num, start_time, end_time):
    menu_headers = {
        'Cookie': cookie,
        'Origin': 'http://www.ygzx.cast',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.ygzx.cast',
        'Referer': 'http://www.ygzx.cast/db/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.43 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',

    }

    data = []
    limit = 5000
    tmParamStr = str(start_time) + '|' + str(end_time) + "|" + str(mid) + "&" + str(telemetry_num) + '&' + str(
        telemetry_id) + '&0|'
    form_data = {
        '_dc': date_stamp,
        'type': 0,
        'timeSpan': 10,
        'tmParamStr': tmParamStr,
        'limit': limit,
        'v1': '',
        'v2': '',
        'page': 1,
        'start': 0,
    }
    post_url = 'http://www.ygzx.cast/db/tmdata/tmdata.edq'
    while 1:
        res = requests.post(url=post_url, headers=menu_headers, data=form_data)
        r_json = hjson.loads(res.text)
        count = r_json['count']
        items = r_json['items']
        s = requests.session()
        s.keep_alive = False
        data = data + items
        if count == 0 or count < limit:
            break
        else:
            # 获取结尾时间
            new_start_time = items[-1]["T0"]
            new_start_time = new_start_time.replace('-', '').replace(' ', '').replace(':', '').replace('.', '')
            form_data["tmParamStr"] = str(new_start_time) + '|' + str(end_time) + "|" + str(mid) + "&" + str(
                telemetry_num) + '&' + str(telemetry_id) + '&0|'

    # with open('crawl.json', 'w', encoding="utf-8") as fp:
    #     fp.write(data)
    # print("写入crawl.json成功")
    return data


def check_login(username, password):
    cookie = get_cookie(username, password)
    date_stamp = int(time.time() * 1000)
    # 解析型号名称
    modellist = crawl_menu(cookie, date_stamp)
    if modellist is None or modellist == []:
        return False
    else:
        return True


def crawl(username, password, model_name, telemetry_name, start_time, end_time):
    start_time = trans_time(start_time)
    end_time = trans_time(end_time)
    cookie = get_cookie(username, password)
    date_stamp = int(time.time() * 1000)
    # 解析型号名称
    modellist = crawl_menu(cookie, date_stamp)
    if modellist is None or modellist == []:
        return False, "账号或密码错误"
    mid = None
    sys_resource_id = None
    for item in modellist:
        if item["name"] == model_name:
            mid = item['mid']
            sys_resource_id = item["sys_resource_id"]
            break
    else:
        return False, "未匹配到型号ID"
    # 解析遥测代号
    telemetry_id = None
    telemetry_num = None
    numlist = find_grant(date_stamp, cookie, sys_resource_id, telemetry_name)
    for item in numlist:
        if item["code"] == telemetry_name:
            telemetry_id = item["id"]
            telemetry_num = item["num"]
            break
    else:
        return False, "未解析到遥测代号"
    # 实际爬取数据
    data = crawldata(date_stamp, cookie, mid, telemetry_id, telemetry_num, start_time, end_time)
    items = parse_data(data)
    return True, items


def create_test_timedata(start_time_str, end_time_str, min_value, max_value):
    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f")
    item = []
    # print((end_time - start_time).total_seconds())
    for i in range(int((end_time - start_time).total_seconds())):
        tmp = start_time + datetime.timedelta(seconds=i)
        item.append({
            "T0": str(tmp),
            "V02317575": random.randint(int(min_value * 100), int(max_value * 100)) / 100
        })

    return item


def crawl_test(satellite_data, model_name, telemetry_name, start_time, end_time):
    # 生成随机数据
    items_1 = create_test_timedata("2020-10-11 18:25:27.454", "2020-10-11 19:25:27.454", -0.15, 0.1)
    items_2 = create_test_timedata("2020-10-11 19:45:27.454", "2020-10-11 21:25:27.454", -0.15, 0.1)
    items = items_1 + items_2
    items[300]["V02317575"] = 0.5
    items[3000]["V02317575"] = -0.5
    items[6000]["V02317575"] = 0.5
    items = parse_data(items)

    satellite_data.add_data(items)
    satellite_data.rename_extension()
    return True, satellite_data


def load_dirty_json(dirty_json):
    import re
    regex_replace = [(r"([ \{,:\[])(u)?'([^']+)'", r'\1"\3"'), (r" False([, \}\]])", r' false\1'),
                     (r" True([, \}\]])", r' true\1')]
    for r, s in regex_replace:
        dirty_json = re.sub(r, s, dirty_json)
    clean_json = json.loads(dirty_json)
    return clean_json


def parse_data(items):
    new_items = collections.OrderedDict()
    for item in items:
        new_k = ''
        new_v = 0.0
        for k, v in item.items():
            if k == 'T0':
                new_k = v
            else:
                new_v = v
            # if type(v) == float:
            #     new_v = v
            # else:
            #     new_k = v
        new_items[new_k] = new_v
    return new_items


def trans_time(time_str):
    # "20201014039500000"
    l = time_str.split(" ")
    s = l[1].split(":")
    d = l[0].replace('/', '-')
    d = ''.join([i if len(i) > 1 else '0' + i for i in d.split('-')])
    h = s[0] if len(s[0]) == 2 else '0' + s[0]
    m = s[1]
    s = '00000'
    new_time = d + h + m + s
    return new_time


if __name__ == '__main__':
    crawl()

# _dc:1602725959757
# type:0
# timeSpan:10
# tmParamStr:2020 10 11 18 09 37428|20201014093500000|4524&10288&2317575&0|
# limit:50
# v1:
# v2:
# page:1
# start:0


# _dc:1602725844140
# type:0
# timeSpan:10
# tmParamStr:2020 10 11 09 35 00000|20201014093500000|4524&10288&2317575&0|
# limit:50
# v1:
# v2:
# page:1
# start:0

# _dc:1602726091193
# type:0
# timeSpan:10
# tmParamStr:202010 11 18 10 26431|202010 14 09 3500000|4524&10288&2317575&0|
# limit:50
# v1:
# v2:
# page:1
# start:0


# {
#     "code": "ALxxxx",
#     "create_time": "2017-12-11 16:34:50.000",
#     "create_user": "2",
#     "leaf": "false",
#     "mid": 7414,
#     "name": "ALxxxxx",
#     "owner_id": "-1",
#     "status": "0",
#     "sys_resource_id": "660792",
#     "type": 0
# },


# {
#     "code": "RKxxxxx",
#     "create_time": "2020-01-15 10:40:31.000",
#     "create_user": "2",
#     "id": 2309770,
#     "name": "滚动角xxxxxx",
#     "num": "10331",
#     "owner_id": "2292081",
#     "sat_id": "2292081",
#     "struct": "->2292081",
#     "tm_param_code": "RKxxxx",
#     "tm_param_id": 2309770,
#     "tm_param_name": "滚动角xxxxx",
#     "tm_param_num": "10331",
#     "tm_param_type": "0",
#     "type": "0"
# },
