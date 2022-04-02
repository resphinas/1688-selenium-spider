# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/9 11:10
@Auth ： wes陈维炜
@File ：utility.py
@IDE ：PyCharm
@email：2934218525@qq.com

"""
"""
工具
作    者: Ed
创建日期: 2021-06-15
上次修改: 2021-06-16
"""
import datetime
import json
import os.path
from typing import (
    List,
    Any
)
import csv

CSV_FILE_PATH = "output/all_data.csv"
ALRAEDY_TXT_FILE_PATH = "already.txt"


def save_json_file(
        data: Any,
        filename: str
) -> None:
    """
    将数据保存到json文件
    :param data:
    :param filename: 带完整路径的文件名
    :return:
    """
    with open(filename, mode="w+", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json_file(
        filename: str
) -> Any:
    """
    去读json文件获取数据
    :param filename: 带完整路径的文件名
    :return:
    """
    if not os.path.isfile(filename):
        raise Exception(filename + " is not a file")
    with open(filename, mode="r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def clear_dir(
        directory: str
) -> None:
    if not os.path.isdir(directory):
        raise Exception(directory + " is not a directory")
    # 如果没有"/"就加上
    if not directory.endswith("/"):
        directory = directory + "/"
    # 遍历删除文件
    files = os.listdir(directory)
    for file in files:
        os.remove(directory + file)


def clear_file(
        filename: str
) -> None:
    """
    清空特定文件
    :param filename:
    :return:
    """
    with open(filename, mode="w") as f:
        f.close()



# 校验文件夹中是否有且仅有一个文件
def if_only_cone_file(
        directory: str
) -> bool:
    """
    校验文件夹中是否有且仅有一个文件
    :param directory: 文件夹名
    :return:
    """
    if not os.path.isdir(directory):
        raise Exception(directory + "is not a directory")
    files = os.listdir(directory)
    if 1 == len(files):
        return True
    else:
        return False

def save_csv_file(
        data
) -> Any:
    """
    把每个品类的商品列表一次存进总数据表里
    第一次判断是否存在 存在则直接添加 不存在则新建且新建表头
    :param e: 带完整路径的文件名
    :return:
    """
    #判断是否存在
    while True:
        try:
            with open(CSV_FILE_PATH, "a+", encoding="utf-8", newline="") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(data)

                break
        except:
            if flag == 0:
                print("警告：请关闭utput/all_data.csv 表 以便程序存储数据表！")
            flag = 1


def already(id):
    with open(ALRAEDY_TXT_FILE_PATH,"a+",encoding="utf-8") as file:
        file.write(str(id) + "\n")

def init_csv_txt_file(
        head_row
) -> Any:
    """
    新建一个csv表
    :param head_row:传进来的表头行列表

    """
    with open(ALRAEDY_TXT_FILE_PATH, "w", encoding="utf-8") as file:
        pass
    flag = 0
    while True:
        try:
            with open(CSV_FILE_PATH,"w",encoding="utf-8",newline="") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(head_row)
                break
        except:
            if flag == 0:
                print("警告：请关闭utput/all_data.csv 表 以便程序存储数据表！")
            flag = 1
