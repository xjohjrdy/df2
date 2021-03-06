# 独立使用django的model
import sys
import os

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "df2.settings")

import django

django.setup()

from app.acc.models import AccManage
from app.car.models import CarInfoManage, CarFixManage, CarFixAccManage, EmployeeBonusManage
from app.staff.models import EmployeeManage

# 分页获取原始数据
import MySQLdb

# connect() 方法用于创建数据库的连接，里面可以指定参数：用户名，密码，主机等信息。
# 这只是连接到了数据库，要想操作数据库需要创建游标。
conn = MySQLdb.connect(
    host='localhost',
    port=3306,
    user='123',
    passwd='23',
    db='db',
    charset='utf8'
)


def acc():
    time = 0
    table = 'form_accmanage'
    cur.execute(count_sql % table)
    count = cur.fetchone()[0]
    while time <= count // n:
        cur.execute(sql_offset % (table, n, n * time))
        values = cur.fetchall()
        acc_list = [
            AccManage(old_id=item[0], common_name=item[1], name=item[2], sn=item[3], type=item[4], location=item[5],
                      cost=item[6], price=item[7], count=item[8], remark=item[9], station_id=item[10]) for item
            in values]
        AccManage.objects.bulk_create(acc_list)
        time += 1


def car_info():
    time = 0
    table = 'form_carinfomanage'
    cur.execute(count_sql % table)
    count = cur.fetchone()[0]
    while time <= count // n:
        cur.execute(sql_offset % (table, n, n * time))
        values = cur.fetchall()
        acc_list = [
            CarInfoManage(old_id=item[0], sn=item[1], number=item[2], type=item[3], but_date=item[4], pro_date=item[5],
                          owner=item[7], tel=item[8], remark=item[9], station_id=item[10]) for item
            in values]
        CarInfoManage.objects.bulk_create(acc_list)
        time += 1


def _get_new_id(old_id, model, id=0):
    try:
        item = model.objects.get(old_id=old_id)
    except Exception as e:
        print(e)
        return 1
    return item.id


def _get_emp(old_id, model):
    try:
        item = model.objects.get(name=old_id)
    except Exception as e:
        print(e)
        return 1
    return item.id


def _get_fix_id(old_fix_id):
    try:
        return CarFixManage.objects.get(old_id=old_fix_id).id
    except Exception as e:
        print(e)
        return 1


a = 446


def _get_acc_id(acc_id, old_fix_id, model):
    global a
    a += 1
    try:
        fix_id = CarFixManage.objects.get(old_id=old_fix_id).id
        item = model.objects.get(id_number=acc_id, fix_id=fix_id)
    except Exception as e:
        print(e)
        return a
    return item.id


def car_fix():
    time = 0
    table = 'form_carfixmanage'
    cur.execute(count_sql % table)
    count = cur.fetchone()[0]
    while time <= count // n:
        cur.execute(sql_offset % (table, n, n * time))
        values = cur.fetchall()
        acc_list = [
            CarFixManage(old_id=item[0], car_id=_get_new_id(item[1], CarInfoManage), odo=item[2], date=item[3],
                         reg_time=item[13], income=item[5],
                         remark=item[8], logging=item[10], maintain=item[11], station_id=item[12]) for item
            in values]
        CarFixManage.objects.bulk_create(acc_list)
        time += 1


def car_acc():
    time = 0
    table = 'form_carfixaccmanage'
    cur.execute(count_sql % table)
    count = cur.fetchone()[0]
    while time <= count // n:
        cur.execute(sql_offset % (table, n, n * time))
        values = cur.fetchall()
        acc_list = [
            CarFixAccManage(old_id=item[0], fix_id=_get_new_id(item[1], CarFixManage, item[4]), name=item[2],
                            id_number=item[3],
                            type=item[4].strip(), price=item[5], usage=item[6], date=item[7], guarantee=item[8],
                            station_id=item[9], cost=item[10]) for item
            in values]
        CarFixAccManage.objects.bulk_create(acc_list)
        time += 1


def bonus():
    time = 0
    table = 'form_employeebonusmanage'
    cur.execute(count_sql % table)
    count = cur.fetchone()[0]
    count = 1
    while time <= count // n:
        cur.execute(sql_offset % (table, n, 257))
        values = cur.fetchall()
        acc_list = [
            EmployeeBonusManage(date=item[1], employee_id=_get_emp(item[2], EmployeeManage),
                                fix_id_id=_get_fix_id(item[3]),
                                acc_id_id=_get_acc_id(item[4], item[3], CarFixAccManage), profit=item[5], bonus=item[6])
            for item
            in values]
        EmployeeBonusManage.objects.bulk_create(acc_list)
        time += 1


if __name__ == '__main__':
    # 通过获取到的数据库连接conn下的cursor()方法来创建游标。
    cur = conn.cursor()
    count_sql = "select count(id) from %s"
    sql_offset = "select * from %s limit %s OFFSET %s"
    n = 100  # 每次查询条数
    try:
        # acc()
        # car_info()
        # car_fix()
        # car_acc()
        bonus()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
