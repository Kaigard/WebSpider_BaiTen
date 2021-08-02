# coding = utf-8
from collections import Counter
import numpy as np
from bs4 import BeautifulSoup
import re
import urllib
import urllib.request
import xlwt
import sqlite3
from selenium import webdriver
from time import sleep
from icecream import ic
from selenium import webdriver
import time
from lxml import etree
import pandas as pd
import jieba

def main():
    cookie = '************************************'
    #初始化存储数组，佰腾网单词条仅爬取2000条数据
    nameData = [0 for i_n in range(100 * 20)]
    petitionerData = [0 for i_p in range(100 * 20)]
    inventorData = [0 for i_i in range(100 * 20)]
    abstractData = [0 for i_a in range(100 * 20)]
    #python左开右闭
    for i_page in range(1, 201):
        baseUrl = "https://www.baiten.cn/results/l/%25E7%259B%25B8%25E6%258E%25A7%25E9%2598%25B5/.html?type=l#/10/" + str(i_page)
        #传入url以及页数
        getData(baseUrl, i_page, petitionerData, inventorData, abstractData, nameData, cookie)

def getData(baseUrl, i_page, prtitionerData, inventorData, abstractData, nameData, cookie):
    #使用selenium库中webdriver函数模拟chrome
    driver = webdriver.Chrome()
    driver.get(baseUrl)
    #以键值对形式添加cookie绕过佰腾网，cookie可变，浏览器开发者工具f12中webnet可查看
    driver.add_cookie({'name':'JSESSIONID', 'value':cookie})
    sleep(3)
    driver.refresh()
    sleep(2)
    #使用bs4模块将网页源码格式转换
    bs = BeautifulSoup(driver.page_source, "lxml")
    #数据爬取
    for i_allData in range(0 + 10 * (i_page - 1), 10 + 10 * (i_page - 1)):
        #以下三个数据皆在一级链接，直接爬取返回即可
        nameData, CN = getNameData(i_allData, nameData, bs, i_page)
        petitionerData = getPetitionerData(i_allData, prtitionerData, bs, i_page)
        inventorData = getInventorData(i_allData, inventorData, bs, i_page)
        #摘要一级链接中选择器不具备规律性，因此选择二级链接进行爬取
        abstractData = getAbstractData(i_allData, abstractData, bs, i_page, baseUrl, cookie, CN)
        #ic打印测试
        ic(nameData[i_allData])
        ic(prtitionerData[i_allData])
        ic(inventorData[i_allData])
        ic(abstractData[i_allData])
    driver.close()
    saveData(nameData, petitionerData, inventorData, abstractData)

def getCN(middleChange1):
    flag1 = 'CN'
    flag2 = '&amp;sc=&amp;'
    #简单的字段截取
    sameData = middleChange1[middleChange1.find(flag1): middleChange1.find(flag2)]
    return sameData

def getNameData(i_allData_name, nameData_name, bs_name, i_page_name):
    #根据佰腾网selector规律设定选择器爬取专利名称及专利号
    nameData_name[i_allData_name] = bs_name.select('#Js_listLoader > div > div.Js_outerList > table > tbody > tr:nth-child(' + str(((i_allData_name + 1) - ((i_page_name - 1) * 10)) * 2) +') > td:nth-child(5) > a')
    #转string格式方便后续处理
    middleChange1 = str(nameData_name[i_allData_name])
    #使用正则化提取标签中的中文信息
    res1 = ''.join(re.findall('[\u4e00-\u9fa5]', middleChange1))
    #将正则化后的中文信息存储回原数组
    nameData_name[i_allData_name] = res1
    CN = getCN(middleChange1)
    return nameData_name, CN

def getPetitionerData(i_allData_petitioner, petitionerData_petitioner, bs_petitioner, i_page_petitioner):
    petitionerData_petitioner[i_allData_petitioner] = bs_petitioner.select('#Js_listLoader > div > div.Js_outerList > table > tbody > tr:nth-child(' + str(((i_allData_petitioner + 1) - ((i_page_petitioner - 1) * 10)) * 2) +') > td:nth-child(9) > a')
    # 转string格式方便后续处理
    middleChange2 = str(petitionerData_petitioner[i_allData_petitioner])
    # 使用正则化提取标签中的中文信息
    res2 = ''.join(re.findall('[\u4e00-\u9fa5]', middleChange2))
    seg = jieba.cut(res2, cut_all=True)
    # 将正则化后的中文信息存储回原数组
    petitionerData_petitioner[i_allData_petitioner] = res2
    return petitionerData_petitioner

def getInventorData(i_allData_inventor, inventorData_inventor, bs_inventor, i_page_inventor):
    inventorData_inventor[i_allData_inventor] = bs_inventor.select('#Js_listLoader > div > div.Js_outerList > table > tbody > tr:nth-child(' + str(((i_allData_inventor + 1) - ((i_page_inventor - 1) * 10)) * 2) +') > td:nth-child(10) > a')
    # 转string格式方便后续处理
    middleChange3 = str(inventorData_inventor[i_allData_inventor])
    # 使用正则化提取标签中的中文信息
    res3 = ''.join(re.findall('[\u4e00-\u9fa5]', middleChange3))
    # 将正则化后的中文信息存储回原数组
    inventorData_inventor[i_allData_inventor] = res3
    return inventorData_inventor

def getAbstractData(i_allData_abstract, abstractData_abstract, bs_abstract, i_page_abstract, baseUrl_abstract, cookie, CN):
    #再次模拟chrome登录
    driver_abstract = webdriver.Chrome()
    CN = str(CN)
    secondUrl = 'https://www.baiten.cn/patent/detail/78d53af61a68c2fbf3575004b527d4a6591d226808506f2c?sc=&fq=&type=&sort=&sortField=&q=pa%3A%28%E5%8D%97%E7%91%9E%29&rows=10#1/' + CN + '/detail/abst'
    driver_abstract.get(secondUrl)
    # 以键值对形式添加cookie绕过佰腾网，cookie可变，浏览器开发者工具f12中webnet可查看
    driver_abstract.add_cookie({'name': 'JSESSIONID', 'value': cookie})
    sleep(3)
    driver_abstract.refresh()
    sleep(2)
    bs_abstract = BeautifulSoup(driver_abstract.page_source, "lxml")
    abstractData_abstract[i_allData_abstract] = bs_abstract.select('#Js_patent_view_container > div > div.fn-clear.Js_patent_view_item.ui-switchable-panel > div.g-info-l > div > div > div.Js_patent_view_content.ui-switchable-content > div:nth-child(1) > div > div.abstract.contenttext')
    # 转string格式方便后续处理
    middleChange4 = str(abstractData_abstract[i_allData_abstract])
    # 使用正则提取标签中的中文信息，且保留标点符号
    res4 = divideWord(middleChange4)
    # 不保留标点符号的正则表达式
    # res4 = ''.join(re.findall('[\u4e00-\u9fa5]', middleChange4))
    # 将正则化后的中文信息存储回原数组
    abstractData_abstract[i_allData_abstract] = res4
    # 关闭driver
    driver_abstract.close()
    return abstractData_abstract

def saveData(nameData, petitionerData, inventorData, abstractData):
    dataFrame = pd.DataFrame({'专利名': nameData,
                              '申请人': petitionerData,
                              '发明人': inventorData,
                              '摘要': abstractData})
    dataFrame.to_excel('build.xlsx')

def divideWord(reWords):
    t = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]', reWords)
    a = ''.join(t)
    return a

if __name__ == "__main__":
    main()



