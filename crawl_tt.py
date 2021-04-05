import requests
import json
from openpyxl import Workbook
import time
import hashlib
import os
import datetime
import random

# 功能函数
class get_tt_title:
    def __init__(self):
        # 伪装成浏览器进行网页登录，设置多个，防止被网站的反爬程序阻止
        self.headers=[
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
]
  
        self.Dirs_Save = './头条爬取内容/'# 文件保存地址
        self.Cookies = {'tt_webid':'6945081525160117791'} # 此处cookies可从浏览器中查找，为了避免被头条禁止爬虫
        self.Tt_url = 'https://www.toutiao.com' # 头条初始网页
        self.Start_url = f'https://www.toutiao.com/api/pc/feed/?category={news_type}&utm_source=toutiao&widen=1&max_behot_time='
        self.Title_Count = 0 # 已爬取的标题数量
        self.Over_Flag = 0 # 爬取结束的标志
        self.Max_Behot_Time = str(round(time.time()))   # 链接参数
        self.Txt_Name = '' # 待保存的文件名
        self.News_Type = '' # 新闻类型
    
    def get_as_cp(self):  # 该函数主要是为了获取as和cp参数，程序参考今日头条中的加密js文件：home_4abea46.js
        zz = {}
        now = round(time.time())
        #print(now) # 获取当前计算机时间
        e = hex(int(now)).upper()[2:] #hex()转换一个整数对象为16进制的字符串表示
        #print('e:', e)
        a = hashlib.md5()  #hashlib.md5().hexdigest()创建hash对象并返回16进制结果
        #print('a:', a)
        a.update(str(int(now)).encode('utf-8'))
        i = a.hexdigest().upper()
        #print('i:', i)
        if len(e)!=8:
            zz = {'as':'479BB4B7254C150',
            'cp':'7E0AC8874BB0985'}
            return zz
        n = i[:5]
        a = i[-5:]
        r = ''
        s = ''
        for i in range(5):
            s= s+n[i]+e[i]
        for j in range(5):
            r = r+e[j+3]+a[j]
        zz ={
        'as':'A1'+s+e[-3:],
        'cp':e[0:3]+r+'E1'
        }
        #print('zz:', zz)
        return zz
   
    def main(self):
    
        # 创建待保存的文件路径
        if not os.path.exists(self.Dirs_Save):
            os.makedirs(self.Dirs_Save)
        # 未爬取完毕则继续爬取
        while self.Over_Flag == 0:
            
            # 延迟访问，防止被反爬发现。可尝试删除以加快爬取速度
            #time.sleep(random.randint(1,3))
            # 获取as和cp参数的函数
            # 不加该段数据也可得到json
            #ascp = self.get_as_cp()    
            #url_to_get = self.Start_url+self.Max_Behot_Time+'&max_behot_time_tmp='+self.Max_Behot_Time+'&tadrequire=true&as='+ascp['as']+'&cp='+ascp['cp']
            url_to_get = f'https://www.toutiao.com/api/pc/feed/?max_behot_time={self.Max_Behot_Time}&category={self.News_Type}&utm_source=toutiao&widen=1&tadrequire=true'
            
            
            # 轮流使用多个不同的User-agent 
            webdata = requests.get(url_to_get, headers=random.choice(self.headers), cookies=self.Cookies)
            #print(url_to_get)
            demo = json.loads(webdata.text)
            

            self.Max_Behot_Time = str(demo['next']['max_behot_time']) 

            # 打开要写入的文件，可续写
            f = open(self.Dirs_Save+self.Txt_Name, 'a', encoding = 'utf-8')
            title = []
            for j in range(len(demo['data'])):
                # 获取新闻标题
                tmp_title = demo['data'][j]['title']
                # 删去非标题部分
                if '\n' in tmp_title:
                    continue
                title.append(tmp_title)  
            
                self.Title_Count += 1
                if self.Title_Count%20 == 0:
                    print(f'已爬取{self.Title_Count}条新闻')
                if self.Title_Count==nums_to_crawl:
                    # 暂停爬取，已爬取足够数量的标题
                    self.Over_Flag = 1
                    break
                
                
                # 新闻链接
                s_url = self.Tt_url+demo['data'][j]['source_url']
            # 将当前存入的标题写入文件
            f.write('\n'.join(title))    
            f.close()

if __name__ == '__main__':
    # 可根据头条新闻类型，扩充该字典
    news_types_dict = {'科技':'news_tech','娱乐':'news_entertainment','游戏':'news_game','体育':'news_sports'}
    while True:
        try:
            news = input('请输入要爬取新闻类型（科技、娱乐、游戏、体育）:')
            news_type = news_types_dict[news]
            break
        except:
            print('请重新输入新闻类型')
            continue
    nums_to_crawl = int(input('请输入要爬取新闻标题数量:'))
    
    
    # 定义类的对象
    crawler = get_tt_title()
    crawler.Txt_Name = f'{news}新闻.txt'
    crawler.News_Type = news_type
    print('开始爬取')
    crawler.main()
    print('爬取结束')
