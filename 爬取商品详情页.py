# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/30 14:23
@Auth ： wes
File ：extract_data.py
@IDE ：PyCharm
@email：2934218525@qq.com
爬取商品详情页 链接在links.txt中

"""
import time

import requests
import re
from bs4 import BeautifulSoup
from utility import  generate_headers
import csv
from  selenium import webdriver
import random
def create_driver(
        show: bool = True
) :
    """
    创建浏览器驱动
    :param show: 是否弹出浏览器页面
    :return: 浏览器驱动
    """
    chrome_options = webdriver.ChromeOptions()
    #打开ip池目录进行随机选择
    with open("ip.txt",'r',encoding="utf-8") as file:
        ori_content = file.read()
        ips = ori_content.strip().split('\n')
    random_ip = random.choice(ips)

    #ip用过之后则在文档中清除
    new_content = ori_content.replace(random_ip,'')

    with open("ip.txt",'w',encoding="utf-8") as file:
       file.write(new_content)

    #给模拟浏览器添加ip
    print("ip已切换！ ",f"--proxy-server=http://{random_ip}")
    # chrome_options.add_argument()
    # chrome_options.add_argument(f"--proxy-server=http://{random_ip}")

    # chrome_options.add_argument(f"--proxy-server=https://{random_ip}")

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

    driver = webdriver.Chrome(options=chrome_options)

    # 执行cdp命令
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                                Object.defineProperty(navigator, 'webdriver', {
                                  get: () => undefined
                                })
                              """
    })

    return driver

driver=  create_driver()

#读取要爬取的链接文档 \n分割
with open("links.txt",'r',encoding="utf-8") as file:
    links_list = file.read().split("\n")



#回溯时用到的索引
num = -1

already_list = links_list
print(already_list)
for i in range(len(links_list)):
    num +=1
    id = re.findall("https://detail.1688.com/offer/(.*?).html", links_list[num])[0]
    print("current id is: {}".format(id))
    if id in already_list:
        print("chack already id {}".format(id))
        continue

    #爬取进度选择
    # if num ==146:
    #     continue
    # if num<147:
    #     continue

    if num<1 :
        num=0
    #请求链接
    driver.get(links_list[num])
    #测试时用
    # driver.get("https://detail.1688.com/offer/656423355656.html")
    # time.sleep(1)
    res = driver.page_source
    print(num,": ",links_list[num])
    try:
        false = False
        ture = True
        #获取商品属性表
        attrbutes = eval(res.split('@ali/tdmod-od-pc-attribute-new","data":')[-1].split('}]')[0] + '}]')
    except Exception as f:
        print(f)
        num-=1
        # print(res)
        print("check0","获取属性表时出错导致跳出  link:{}".format(links_list[num]))
        input()
        # driver.close()
        # driver = create_driver()

        continue
    try:
        images_urls =eval('{"name":' + res.split('\\"value\\":[{\\"name\\":\\')[1].split('prop')[0][:-4].replace("\\",""))
    except:
        images_urls = ("无","无")
    try:

        other_images_urls = eval(res.split('{"offerImgList":')[1].split(']')[0]+']')
        # print(res)
        # print("\n\n\n\n\n",other_images_urls)
        # input()
    except Exception as p:
        print("获取other_images_urls 时出错")
        pass
    false = False
    true = True

    try:
        uniweight = re.findall('"unitWeight":(.*?),',res)[-1]
    except:
        uniweight= "无"
    # print(res)mn"
    details_url = re.findall('"detailUrl\\":\\"(.*?)\\"',res)[0]


    # print(details_url)
    details = """"""

    try:
        #获取商品详情页的文字叙述部分 这里是嵌套了一个单独的html

        detail_res = requests.session().get(details_url).text
        #正则清晰取出纯html后用解析器提取出纯文本
        detail_res = detail_res.split('var offer_details={"content":"')[-1].split('"};')[0]
        #做下特殊的封装让xml解析器辨认
        s = f"""
        <!DOCTYPE html>
        <html>
        <body>
        
        {detail_res}

        </body>

        </html>

        """
        #解析出纯文本
        soup = BeautifulSoup(detail_res)
        txt = soup.get_text()
        with open(f"details/{id}.txt","w",encoding="gbk") as file:
            file.write(detail_res)
        # non = re.findall('<(.*?)>',detail_res)
    #     for i in non:
    #         if len(i) >= 300:
    #             continue
    #         detail_res = detail_res.replace("<"+i+">","").replace("&nbsp","").replace('var offer_details={"content":"',"").replace("};","").replace(";",'').replace('"'," ")

        # detail_list = re.findall('">(.*?)<span',detail_res)
        # for si in detail_list:
        #     details += si + "\n"
        # print(de"tails)
        # input("fawnafknbfanwfna")
        # print(details)
        # input()
    except Exception as f:
        print(f)
        print("获取详情页content时出问题")
        # input()

    # input("fawhfhadf")
    # input()
    # print(res)
    # print(images_urls)
    # print(other_images_urls)
    # print(attrbutes,"\n\n")
    # print(uniweight)
    # print(images_urls)

    # input()

    # id = re.findall("https://detail.1688.com/offer/(.*?).html",links_list[num])[0]

#         csv_file = csv.writer(file)
# csv_file.writerow(['id','单位重量','图链接','型号/颜色'])
    attrbutes_string = """"""
    for k in attrbutes:
        attrbutes_string += f"{k['name']}:{k['value']}+\n"
    other = """"""
    for k in other_images_urls:
        other += k+"\n"
    for j in range(len(images_urls)):
        with open("goods_detail_information.csv", "a+", encoding="gbk", newline='',errors="ignore") as file:

            csv_file = csv.writer(file)
            need = []
            need.append(id)

            need.append(uniweight)
            # print(res)
            if images_urls != ("无","无"):
                try:
                    need.append(images_urls[j]['name'])
                    need.append(images_urls[j]['imageUrl'])
                except:
                    print(images_urls)
                    try:
                        need.append(images_urls['name'])
                        try:
                            need.append(images_urls['imageUrl'])
                        except:need.append("无")
                    except:
                        need.append(images_urls[j]['name'])
                        need.append("无")
            else:
                need.append("无")
                need.append("无")

            need.append(other)
            need.append(attrbutes_string)
            need.append(txt)
            print("写入的列表如下:")
            print(need)
            csv_file.writerow(need)

    # break
