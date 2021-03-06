#!/usr/bin/env python
# -*- coding:utf-8 -*-


# Time: 2019/3/6 8:44
__author__ = 'Peter.Fang'

import os
import sys
import requests
import datetime
import subprocess

s = requests.session()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = [
    ('serverName', 'dcms.dfsk.com.cn'),
    ('visistBrowser', 'CHROME'),
    ('visistVersion', '68.0.3440.106'),
    ('userName', 'F13-0009_HGH'),
    ('pwd', '1234qwer'),
]
data_Location = [
    ('deptId', ''),
    ('poseId', ''),
]

data_VIN = [
    ('VIN', ''),
    ('lastLoginUserName', 'F13-0009_HGH'),
]

data_VIN_DETAIL = [
    ('VIN', 'LVZA53P90FC641821'),
    ('_JSON_PARAMS_', ''),
]

today = datetime.datetime.now().strftime('%Y-%m-%d')


def parse_info_html(res):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(res.text, 'html.parser')
    format = ["number", "type", "buy_date", "pro_date", "owner", "tel"]
    number = soup.find(name='input', attrs={"id": "LICENSE_NOID"}).get('value')
    car_type = soup.find(name='td', text={"物料："}).findNext('td').contents[0]
    buy_date = soup.find(name='td', text={"购车日期："}).findNext('td').contents[0].strip()
    pro_date = soup.find(name='td', text={"生产日期："}).findNext('td').contents[0].strip()
    owner = soup.find(name='td', text={"车主姓名："}).findNext('td').contents[0].strip()
    tel = soup.find(name='td', text={"车主电话："}).findNext('td').contents[0].strip()
    data = (number, car_type, buy_date, pro_date, owner, tel)
    return {k: v for k, v in zip(format, data)}


def login(acc_flag=False):
    s.post("http://dcms.dfsk.com.cn/DCMS/common/login/LoginManager/doLogin.json", data)
    if not acc_flag:
        s.post("http://dcms.dfsk.com.cn/DCMS/common/menu/MenuShow/menuDisplay.do?poseId=1100013086",
               data_Location)
    else:
        s.post("http://dcms.dfsk.com.cn/DCMS/common/menu/MenuShow/menuDisplay.do?poseId=1100013083",
               data_Location)


def get_info(VIN):
    login()
    data_VIN = [
        ('VIN', VIN),
        ('lastLoginUserName', 'F13-0009_HGH'),
    ]
    r = s.post("http://dcms.dfsk.com.cn/DCMS/servicemng/businessreception/CustomerReception/vinSelect.json", data_VIN)
    if 'vin:' in r.text:
        temp1 = r.text.split('vin:')
        temp2 = temp1[1].split('"')
        data_VIN_DETAIL = [
            ('VIN', temp2[1]),
            ('_JSON_PARAMS_', ''),
        ]

        r = s.post(
            "http://dcms.dfsk.com.cn/DCMS/servicemng/businessreception/CustomerReception/repairOrderAddInit.do?lastLoginUserName=F13-0009_HGH",
            data_VIN_DETAIL)
        if VIN in r.text:
            return parse_info_html(r)


def get_gurantee(day_start, day_end):
    login()
    s.get(
        'http://dcms.dfsk.com.cn/DCMS/sysmng/usemng/DcsFuncMapping/pageIntegration.do?funcId=88888888')
    s.get(
        'http://idcs.dfsk.com.cn/sysusermng/sysuserinfo/DcsFuncMapping/pageIntegration1.do?funcId=1e4ad363503a24b210130103&password=*********************************&vin=null&inMileage=null&codes=null&codes_type=null&labcodes=null&labcodes_type=null')
    data_download = [
        ('RO_STARTDATE', day_start),
        ('RO_ENDDATE', day_end),
    ]
    r = s.post(
        'http://idcs.dfsk.com.cn/claim/dealerClaimMng/ClaimBillTrack/export.do', data_download)
    with open(os.path.join(BASE_DIR, 'db_tools/data/download_gurantee.xls'), 'wb') as f:
        f.write(r.content)

    # 导入db
    subprocess.run(
        ['/home/fangyu/Venv/df2/bin/python', os.path.join(BASE_DIR, 'db_tools/gurantee_sync.py'), day_start, day_end])


def do_sync_gurantee(day_start=None, day_end=None):
    if not day_start:
        day_start = (datetime.date.today() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    if not day_end:
        day_end = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    get_gurantee(day_start, day_end)


def do_sync_acc_record():
    day_start = (datetime.date.today() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    day_end = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    login(True)
    s.get(
        'http://dcms.dfsk.com.cn/DCMS/sysmng/usemng/DcsFuncMapping/pageIntegration.do?funcId=88888888')
    s.get(
        'http://idcs.dfsk.com.cn/sysusermng/sysuserinfo/DcsFuncMapping/pageIntegration1.do?funcId=1e4ad363503a24b210130103&password=*********************************&vin=null&inMileage=null&codes=null&codes_type=null&labcodes=null&labcodes_type=null')
    data_download = [
        ('RO_STARTDATE', day_start),
        ('RO_ENDDATE', day_end),
    ]
    # 下载excel
    r = s.post(
        'http://idcs.dfsk.com.cn/claim/dealerClaimMng/ClaimBillTrack/export.do', data_download)
    with open(os.path.join(BASE_DIR, 'db_tools/data/test_acc.xls'), 'wb') as f:
        f.write(r.content)

    # 导入db
    subprocess.run(
        ['/home/fangyu/Venv/df2/bin/python', os.path.join(BASE_DIR, 'db_tools/acc_buy_record.py'), day_start, day_end])


func_map = {
    "do_sync_gurantee": do_sync_gurantee,
    "do_sync_acc_record": do_sync_acc_record,
}

if __name__ == "__main__":
    try:
        _, func_key = sys.argv
        func_map[func_key]()
    except ValueError as e:
        print("no func_key")
    except KeyError as e:
        print("func_key is not exist")
