#!/usr/bin.env python
# -*- coding:utf-8 -*-
# author:Qin Ziqiu
# date:2021-04-05
import requests
from lxml import etree
import re,os,random

def page_to_url( page, url0):
    # 将输入的数字转化为字符串，以供组成网址
    numpage = int(page)
    urls = [url0]

    # 根据输入页码生成对应的网址
    for i in range(2, numpage + 1):
        url = url0.replace(".htm", f"_{i}.htm")
        urls.append(url)
    return urls

#print(page_to_url(10,"https://tech.gmw.cn/node_5557.htm"))

headers=[
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
]
def parse_url(url,headers):
    # 从指定网页url的内容读入到webdata中，以供分析使用
    webdata = requests.get(url, headers=random.choice(headers))
    # 通过xpath模块来分析网页内容
    selector = etree.HTML(webdata.text)
    return selector
#print(parse_url("https://tech.gmw.cn/node_5557.htm",headers))

def get_list_page(selector):
    #每个类别都有1-10页内容，每页上又有不同新闻标题组成的列表，点击某个标题才能查看原文，获取正文
    titles = selector.xpath('//*[@class="main_list"]/div/h1/a/text()')
    #防止中文乱码
    titles=[i.encode('ISO-8859-1').decode('utf-8') for i in titles]
    #获取每篇新闻的详情网址
    urls = selector.xpath('//*[@class="main_list"]/div/h1/a/@href')
    return titles,urls

# selector=parse_url("https://tech.gmw.cn/node_5557.htm",headers)
# print(get_list_page(selector))

def get_list_indiv(selector):
    #获取新闻详情页的标题，正文，以及关键字
    titles = selector.xpath('/html/body/div[6]/div[1]/h1/text()')
    titles=[i.encode('ISO-8859-1').decode('utf-8') for i in titles]
    title = ''
    # 标题可能为两行
    for line in titles:
        title += line

    paragraphs = selector.xpath('//*[@id="article_inbox"]/div[6]/p/text()')
    paragraphs=[i.encode('ISO-8859-1').decode('utf-8') for i in paragraphs]

#关键字藏在html的备注中，需要用正则提取，再转化为列表储存。
    # 'enpproperty <articleid>34735894</articleid><date>2021-04-02 10:22:36.0</date><author></author><title>人类最远的“亲戚”找到了</title><keyword>亲戚,栉水母,人类,系统发育关系,自然—通讯</keyword><subtitle></subtitle><introtitle></introtitle><siteid>2</siteid><nodeid>5557</nodeid><nodename>综合新闻</nodename><nodesearchname></nodesearchname>/enpproperty'

    keywords = selector.xpath('//*[@id="article_inbox"]/div[6]/comment()[1]')[0].text
    keywords = keywords.encode('ISO-8859-1').decode('utf-8')
    pattern = r"<keyword>.*?</keyword>"
    keywords = re.search(pattern, keywords).group()
    keywords = keywords.replace('<keyword>', '').replace('</keyword>', '').split(',')
    return title,paragraphs,keywords

# selector=parse_url("https://tech.gmw.cn/2021-04/02/content_34735894.htm",headers)
# print(get_list_indiv(selector))

