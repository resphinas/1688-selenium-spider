# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/21 18:28
@Auth ： wes
@File ：1688_goods_spider.py
@IDE ：PyCharm
@email：

"""
import time
import json
import requests
import re
from utility import  generate_headers
import urllib.parse
import csv
from jsonsearch import JsonSearch
from seleniumwire import webdriver
from tkinter import messagebox

from browsermobproxy import Server
from requests.cookies import RequestsCookieJar
from selenium.webdriver import ActionChains


def save_cookies():
    cookies = driver.get_cookies()
    #获取cookies并保存
    with open("cookies.txt", "w") as fp:
        json.dump(cookies, fp)


def create_driver(
        show: bool = True
) :
    """
    创建浏览器驱动
    :param show: 是否弹出浏览器页面
    :return: 浏览器驱动
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    prefs = {
        'profile.default_content_setting_values':
            {
                'notifications': 2
            },
        'profile.password_manager_enabled': False,
        'credentials_enable_service': False
    }
    chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    if not show:
        chrome_options.add_argument("--headless")

    # 开发者模式防止被识别出
    # 网址：https://blog.csdn.net/dslkfajoaijfdoj/article/details/109146051
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('w3c', False)
    caps = {
        'browserName': 'chrome',
        'loggingPrefs': {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
        },
        'goog:chromeOptions': {
            'perfLoggingPrefs': {
                'enableNetwork': True,
            },
            'w3c': False,
        },
    }
    driver = webdriver.Chrome(desired_capabilities= caps,options=chrome_options)

    # 执行cdp命令
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                                Object.defineProperty(navigator, 'webdriver', {
                                  get: () => undefined
                                })
                              """
    })

    return driver
def find_element_exists(xpath_,flag=0,erro_warning = """"""):
    """
    flag为0时  采用循环定位知道元素存在
    flag为1时，仅判断元素存在与否
    默认为0时无需传参
    :param xpath_: 元素xpath路径
    :param flag:int
    :return:
    """
    if flag==0:
        while True:
            try:
                ele = driver.find_element_by_xpath(xpath_)
                return ele
            except Exception as file:
                print(file)
                print(erro_warning)
                time.sleep(1)
    else:
        try:
            ele = driver.find_element_by_xpath(xpath_)
            return ele
        except Exception as file:
            return False


def get_goods_json(url):
        while True:
            try:
                driver.get(url)
                #程序继续运行所必要的网页条件筛选 在未加载出来之前不执行之后的命令
                find_element_exists('//*[@id="alisearch-input"]',"请手动跳过验证码进行下一步操作")
                #写入js 滑动脚本 模拟人工滑动 加载出ajax 请求
                js = "var q=document.documentElement.scrollTop=10000"
                time.sleep(1)

                driver.execute_script(js)
                time.sleep(2)
                driver.execute_script(js)
                #加载完之后需要一定程度的延迟 否则获取日志时报错
                time.sleep(5)
                #这一部分是网页原生加载的请求 无需ajax 包括20个商品
                content = '{"code":200,"data":{"asyncConfig":{"async":false,"asyncCount":20,"asyncUrl"' + driver.page_source.split(
                    'window.data.offerresultData = successDataCheck({"code":200,"data":{"asyncConfig":{"async":false,"asyncCount":20,"asyncUrl"')[
                    -1]

                check_num = re.findall('"ok","time":(.*?)}',content)[0]
                # print(check_num,'"ok","time":' + str(check_num) +'});')
                # input()
                content = content.split('"ok","time":' + str(check_num) +'});')[0] + '"ok","time":' + str(check_num) +'}'


                #抓selenium的network内置日志
                two_ajax = []
                #去selenium日志中查看遍历所有http请求并且配和js滚动提取需要的ajax
                for entry in driver.get_log('performance'):
                    si = json.loads(entry['message'])
                    si = JsonSearch(object=si, mode='j')
                    try:
                        request_id = si.search_all_value(key='requestId')[-1]
                    except:
                        continue
                    try:
                        #寻找是否是带有url的网络请求 不是则跳过
                        url = si.search_all_value(key='url')[-1]
                    except:
                        continue
                    #匹配所需要寻找的ajax请求 匹配则继续
                    if "asyncCount=20&pageSize=60" not in url:
                        continue
                    else:
                        pass
                        # print(str(url))

                    excluded = []
                    try :
                        #执行命令 获取得到的requestid的具体返回值
                        session_infor = driver.execute("executeCdpCommand",
                                                       {'cmd': 'Network.getResponseBody', 'params': {'requestId': request_id}})['value']
                        print(type(session_infor['body']))
                        true = True
                        false = False
                        # d = JsonSearch(object=eval(str(session_infor['body'])), mode='j')
                        ajax = JsonSearch(object=eval(str(session_infor['body'])), mode='j')
                        ori_ajax = str(session_infor['body'])

                        # print(session_infor,type)
                        index = ajax.search_all_value(key="startIndex")[0]
                        if index not in excluded:
                            excluded.append(index)
                            two_ajax.append(ori_ajax)
                        else:
                            continue
                        print(index)
                    except Exception as file:
                        print(file)
                return [content, two_ajax[0], two_ajax[2]]
            except:
                input("请手动跳过验证码之后按回车键进行下一步操作")
                #取日志ajax失败时重新加载页面，一般只考虑出现各类验证码场景时用
                continue


def login(choice):
    global driver,headers

    driver.get('https://login.taobao.com/?https://login.taobao.com/?redirect_url=https%3A%2F%2Flogin.1688.com%2Fmember%2Fjump.htm%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252FmarketSigninJump.htm%253FDone%253D%25252F%25252Fdetail.1688.com%25252Foffer%25252F564418418427.html&style=tao_custom&from=1688web')

    if choice.strip() == "1":
        #输入账号
        user = input("请输入用户名")
        find_element_exists('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[1]/div[2]/input').send_keys("user")
        time.sleep(1)

        #输入密码
        password = input("请输入密码")
        find_element_exists('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[2]/div[2]/input').send_keys(password)
        #点击登录按钮
        find_element_exists('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div/form/div[4]/button').click()
        # print(driver.page_source)
        # input("check")
    else:
        input("请在扫码后按回车键继续")
    #暂时弃用 玩不过1688的滑块验证 只能往换ip的思路着手
    # if "请按住滑块，拖动到最右边" in driver.page_source:
    #     #用来二次定位的图片元素
    #     ele = find_element_exists('//*[@id="bg-img"]',flag = 1)
    #     if  ele:
    #         ActionChains(driver).move_to_element_with_offset(ele, -46,-332).context_click().perform()
    #         input('check001')
    #目前用不到de cookies存储 备用
    save_cookies()




def get_cookies():
    cookies_dict = dict()
    with open("cookies.txt", "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict

choice = input("请输入登录方式:\n\t1.账号密码自动登录\n\t2.自助扫码登录\n\n")

driver = create_driver()
login(choice)
for sort_type in ["综合搜索","成交量搜索"]:
    keyword = "自行车配件"
    #打开文件便于后续存储
    file = open(f"{keyword}_{sort_type}.csv", "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(file)
    head = ['搜索关键词','id', '价格', '标题', '加红标题', '成交额', '复购率', '搜索页面链接','商品链接', '企业名称', 'consultantscores', 'returnscore', 'quality_experiences', 'disputescores', 'expressscores', '综合服务星级']
    csv_writer.writerow(head)
    uncode_keyword = urllib.parse.quote(keyword.encode('gb2312'))
    for page_num in [1,2]:
            if sort_type =="综合搜索":
                url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={uncode_keyword}&beginPage={page_num}#sm-filtbar"
            else:
                # 按成交额进行排序的商品json信息
                url = f"https://s.1688.com/selloffer/offer_search.htm?&keywords={uncode_keyword}&beginPage={page_num}&sortType=va_rmdarkgmv30&descendOrder=true&uniqfield=userid&n=y#sm-filtbar"
            print(f"page: {page_num}")

            #传回三个原始字符串json  第一个是页面原有的  第二第三个系ajax生成
            res_3 = get_goods_json(url)
            #回溯索引
            num1 = -1
            #回溯标志 初始化为0 值为1时代表需要回溯
            num1_flag = 0
            for res_ in res_3:
                num1+=1
                # print(res.text)
                false= False
                true = True
                null = None
                res_json=eval(res_)
                    #循环三次加载的循环(60 个商品被分为三次请求)
                jsondata = JsonSearch(object=res_json, mode='j')
            #获取json商品中列表  一次20
                while True:
                    try:
                        #解析出需要用到的json
                        all = jsondata.search_all_value(key='offerList')[-1]

                        break
                    except:
                        #在查询下一个链接是出现验证码的处理,人工操控后按回车继续
                        driver.refresh()
                        input("请手动通过验证码成功后按回车")
                        res_3 = get_goods_json(url)
                        num1-=1
                        num1_flag = 1
                        # 获取json商品中列表  一次20
                        break
                if num1_flag:
                    continue

                #获取公司名
                companies = jsondata.search_all_value(key='hoverName')
                #获取价格
                prices = jsondata.search_all_value(key='price')
                #获取商品标题
                titles = jsondata.search_all_value(key='simpleSubject')
                #获取商品红色标题(这里是原始数据)
                red_titles_origins = jsondata.search_all_value(key='subject')
                #咨询评分
                consultantscores = jsondata.search_all_value(key='consultationScore')
                #物流评分
                expressscores = jsondata.search_all_value(key='logisticsScore')
                #质量评分
                quality_experiences = jsondata.search_all_value(key='goodsScore')
                #纠纷评分
                disputescores = jsondata.search_all_value(key='disputeScore')
                #综合评分
                totalscores = jsondata.search_all_value(key= 'compositeNewScore')
                #是否展现复购率的标志
                ifres = jsondata.search_all_value(key= 'showShopRepurchaseRate')

                red_titles = []
                #遍历原始标题取出红色html标签
                for i in red_titles_origins:
                    reds = re.findall("<font color=red>(.*?)</font>",i)
                    if len(reds) != 0:
                        red_titles.append(" ".join(reds))
                    else:
                        red_titles.append(' ')

                for k in range(len(titles)):
                    #判断部分值无效时设置为空（如界面内部分广告产品）
                    rePurchaseRate = all[k]['company']["shopRepurchaseRate"]

                    try:
                        regCapitalUnit = all[k]["tradeQuantity"]["gmvValueFuzzify"]["integer"]
                    except:
                        regCapitalUnit="无"

                    try:
                        id = all[k]["id"]
                    except:

                        id ="无"

                    if id != "无":
                        self_url = f"https://detail.1688.com/offer/{id}.html"
                    else:
                        self_url = "无"


                    try:
                        returnscore = all[k]["tradeService"]["returnScore"]
                    except:
                        returnscore="无"

                    if str(rePurchaseRate) =="0.0":
                        rePurchaseRate ="无"

                    if str(returnscore) =="-1.0":
                        returnscore ="无"

                    if sort_type =="综合搜索":
                        dad_url = f"https://s.1688.com/selloffer/offer_search.htm?spm=a26352.13672862.filtbar.9.27ed5860tLwp6H&keywords={uncode_keyword}&beginPage=1&sortType=normal&descendOrder=true&uniqfield=userid&n=y#sm-filtbar"
                    else:
                        dad_url = f"https://s.1688.com/selloffer/offer_search.htm?spm=a26352.13672862.filtbar.9.27ed5860tLwp6H&keywords={uncode_keyword}&beginPage=1&sortType=va_rmdarkgmv30&descendOrder=true&uniqfield=userid&n=y#sm-filtbar"
                    if regCapitalUnit =="":
                        regCapitalUnit ="无"
                    if rePurchaseRate =="":
                        rePurchaseRate ="无"
                    #必要的行纠错,便于排查
                    prices[k]
                    titles[k]
                    red_titles[k]
                    companies[k]
                    consultantscores[k]
                    quality_experiences[k]
                    disputescores[k]
                    expressscores[k]
                    totalscores[k]
                    print(ifres[k])
                    #定义存入csv的列表
                    row = [keyword,id,prices[k],titles[k],red_titles[k],regCapitalUnit,rePurchaseRate,dad_url,self_url,companies[k],consultantscores[k],returnscore,quality_experiences[k],disputescores[k],expressscores[k],totalscores[k]]
                    print(row)

                    # input("检查单页正确性 调试用")

                    #写入csv 一个简单的容错文件占用循环
                    while True:
                        try:
                            csv_writer.writerow(row)
                            break
                        except:
                            print("程序运行期间不可打开特定写入表格,请及时关闭等待程序运行.")
                    #页数增加传入下一个循环

    file.close()
