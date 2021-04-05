# 导入模块
import requests
from lxml import etree
import re,os,random

# 功能函数
class get_txt_img:
    def __init__(self):
        # 伪装成浏览器进行网页登录
        self.headers=[
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
]       # 文件保存地址
        self.Dirs_Save = './光明网爬取内容/'
        self.Date_Begin = 20201001
        self.Date_End = 20201001

    # 输入日期，获取其第二天的日期，如输入20201001  输出20201002
    def get_next_date(self,date):
        year = date//10000
        month = date//100%100
        date = date%100
        # 判断日期是否大于31号
        if date < 31:
            date +=1
        # 大于，则进入下个月
        else:
            date = 1
            # 判断月份是否大于12
            if month < 12:
                month +=1
            # 大于，则进入下一年
            else:
                month = 1
                year += 1

        next_date = year*10000 + month*100 + date
        return next_date
    
    
    def date_to_url(self,date):
        #https://epaper.gmw.cn/gmrb/html/2021-03/10/nw.D110000gmrb_20210310_1-01.htm
        #https://epaper.gmw.cn/gmrb/html/2021-03/09/nw.D110000gmrb_20210309_1-01.htm

        # 网址中段需要根据输入的年月日进行转换    
        # 将输入的数字转化为字符串，以供组成网址
        year = str(date)[:4]    
        # 小于10的月份格式为0+月份，大于等于10的月份不变。如5月为05,11月为11
        month = str(date)[4:6]  
        # 小于10的日期格式为0+日期，大于等于10的日期不变。如3号为03,15号为15
        day = str(date)[6:]  

        # 根据年月日生成对应的网址
        url = f'https://epaper.gmw.cn/gmrb/html/{year}-{month}/{day}/nw.D110000gmrb_{year}{month}{day}_1-01.htm'
        return url
    
    def parse_url(self,url):
        # 从指定网页url的内容读入到webdata中，以供分析使用
        webdata = requests.get(url, headers=random.choice(self.headers))#random.choice(self.headers)
        # 通过xpath模块来分析网页内容
        selector = etree.HTML(webdata.text)
        return selector
    
    
    def check_name(self,s_name):
        """处理文件名非法字符的方法"""
        s_name = s_name.replace(' ','-')
        pattern = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'

        new_name = re.sub(pattern, "_", s_name)  # 替换为下划线
        return new_name

    def get_title(self,selector):
        titles = selector.xpath('//*[@class="text_c"]/h1/text()')
        title = ''
        # 标题可能为两行
        for line in titles:
            title += line
        #print(title)
        return title

    def save_to_txt(self,selector,txt_name):
        # 获取文章内容
        text_list = selector.xpath('//*[@id="articleContent"]/p/text()')
        f = open(txt_name, 'w', encoding = 'utf-8')
        
        f.write('\n'.join(text_list))
        f.close()
        '''
        for text in text_list:
            text = text.replace('\xa0','')
            f.write(text)  
        '''
          
        print(f'已保存  {txt_name}')    
        
            
    # 获取所有图片的地址
    def get_img_url_list(self,selector):
        img_url_part = selector.xpath('//*[@class="imgBox"]/img/@src')
        if len(img_url_part) > 0: # 本页有图片
            return img_url_part
        else:
            # 本页无图片
            return -1
    
    # 下载图片
    def download_img(self,url,img_url_list,img_name):
        if img_url_list == -1:
            print('本页无图片')
            return -1
        img_num = 1
        for img_url_part in img_url_list:
            img_url = url + '/../' + img_url_part
            # 根据图片地址，获取图片数据
            imgdata = requests.get(img_url, headers=random.choice(self.headers)).content#
            # 为多张图片分别命名
            save_name = img_name + f'{img_num}.jpg'
            img_num +=1
            # 写入图片
            f = open(save_name,'wb')
            f.write(imgdata)
            print(f'已保存  {save_name}')    
            
            
         
if __name__ == '__main__':

    # 日期格式为yyyymmdd  如2020年10月1日：20201001
    # 输入要爬取的起始日期
    date_begin = int(input('请输入要爬取起始日期（格式如：20000101）:'))
    # 输入爬取的结束日期
    date_end = int(input('请输入要爬取结束日期（格式如：20000102）:'))
    # 定义类的对象
    crawler = get_txt_img()
    # 创建待保存的文件路径
    if not os.path.exists(crawler.Dirs_Save):
        os.makedirs(crawler.Dirs_Save)
    # 开始爬取的日期
    crawler.Date_Begin = date_begin
    # 结束爬取的日期
    crawler.Date_End = date_end
    # 开始爬取
    date = crawler.Date_Begin
    # 未爬取到截止日期则继续爬取
    while date <= crawler.Date_End:
        try:
            # 根据日期生成待爬取的网址
            url = crawler.date_to_url(date)
            #print(url)
            # 分析该网址
            selector = crawler.parse_url(url)
            
            # 获得当天头版头条的标题（原始标题）
            name_unchecked = crawler.get_title(selector)
            # 将原始标题处理为可保存的形式
            title = crawler.check_name(name_unchecked)
            # 文件名为保存路径+标题名称
            txt_name = crawler.Dirs_Save + f'{title}.txt'
            # 将文章内容保存到对应的标题文件中
            crawler.save_to_txt(selector,txt_name)

            # 获取该页所有图片的地址
            img_url_list = crawler.get_img_url_list(selector)
            # 图片可能有多张
            img_name = crawler.Dirs_Save + title 
            # 下载图片，该页无图片则提示
            crawler.download_img(url,img_url_list,img_name)
            # 
            date = crawler.get_next_date(date)
        except:
            print('日期输入有误')
            pass    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    