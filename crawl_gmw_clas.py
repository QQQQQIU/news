# 导入模块
import requests
from lxml import etree
import re,os,random

# 功能函数
class get_txt_img_keyw:
    def __init__(self):
        # 伪装成浏览器进行网页登录
        self.headers=[
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
]       # 文件保存地址
        self.Dirs_Save = './光明网分类/'
        self.clas={"经济":"https://economy.gmw.cn/node_8971.htm",
                   "金融":"https://finance.gmw.cn/node_42534.htm",
                   "教育":"https://edu.gmw.cn/node_10602.htm",
                   "军事":"https://mil.gmw.cn/node_8986.htm",
                   "体育":"https://sports.gmw.cn/node_9641.htm",
                   "娱乐":"https://e.gmw.cn/node_7511.htm",
                   "科技":"https://tech.gmw.cn/node_5557.htm",}

    def page_to_url(self,page,url0):
        # 将输入的数字转化为整数，以供组成网址
        numpage = int(page)
        urls=[url0]

        # 根据输入页码生成对应的网址，存入网址列表
        for i in range(2,numpage+1):
            url = url0.replace(".htm", f"_{i}.htm")
            urls.append(url)
        return urls
    
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

    def get_list_whole(self,selector):
        titles = selector.xpath('//*[@id="cont34729353"]/h1/a/text()')
        urls=selector.xpath('//*[@id="cont34729353"]/h1/a/@href')
        title = ''
        # 标题可能为两行
        for line in titles:
            title += line
        #print(title)
        return title

    def get_list_indiv(self,selector):
        titles = selector.xpath('/html/body/div[6]/div[1]/h1/text()')
        paragraphs=selector.xpath('//*[@id="article_inbox"]/div[6]/text()')
        keywords = selector.xpath('//*[@id="article_inbox"]/div[6]/comment()[1]')
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
    crawler = get_txt_img_keyw()
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    