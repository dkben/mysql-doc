#!/usr/bin/python
# coding=UTF-8

import os
import subprocess
import sys
import pymysql.cursors
import yaml
import export_docx


with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

host = cfg['db']['host']
user = cfg['db']['user']
password = cfg['db']['password']
dbName = cfg['db']['db']

tableList = {}

# git_remote = 'git@203.75.119.252:ben/mysql-doc.git'

if not os.path.exists('doc'):
    os.makedirs('doc')


try:
    connections = {
        'conn': pymysql.connect(host=host,
                                user=user,
                                password=password,
                                db=dbName,
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor),
    }
except pymysql.err.OperationalError as e:
    print("Error: 資料庫連線異常...")
    sys.exit()


def get_tables_and_comment():
    cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema='" + dbName + "'")
    tables = cursor.fetchall()
    for table in tables:
        # print(table["TABLE_NAME"])
        # print(table["TABLE_COMMENT"])
        # sys.exit()
        cursor.execute("SHOW FULL columns FROM " + table["TABLE_NAME"])
        columns = cursor.fetchall()
        tableList.update({table["TABLE_NAME"] + ": " + table["TABLE_COMMENT"]: columns})


def check_update():
    check = str(input('是否檢查更新？y 檢查更新 / n 繼續...[y/n]:'))
    if check == 'y':
        print('檢查更新中...')
        local_hash = subprocess.check_output('git log --pretty="%h" -n1 HEAD'.split()).decode()[1:8]
        remote_hash = subprocess.check_output(
            ('git ls-remote %s HEAD' % git_remote).split()).decode()[0:7]
        print(local_hash, remote_hash)
        if local_hash != remote_hash:
            skip = str(input('有新版程式，請 git pull 更新...，按 y 繼續 / n 離開程式...[y/n]:'))
            if skip == 'n':
                sys.exit()
        else:
            input('已經是最新版...按任意鍵繼續...')


def main():
    # print("============================================================")
    # check_update()
    print("============================================================")
    print("開始讀取資料庫並建立檔案...")
    get_tables_and_comment()
    export_docx.create(tableList)


if __name__ == '__main__':
    try:
        with connections["conn"].cursor() as cursor:
            main()
    finally:
        connections["conn"].close()
