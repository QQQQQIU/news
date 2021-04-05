import requests
from lxml import etree
import re,os
import random

class get_book_content:
    def __init__(self):
        # 伪装成chrome浏览器进行网页登录
        self.headers=[
{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
{'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
{'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
]        # 该网页含有多本小说，用于翻页
        self.Start_Url = 'https://www.qidian.com/free/all?orderId=&vip=hidden&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=1&page=1'
        # 文件保存地址
        self.Dirs_Save = './起点中文网爬取内容/'
        
        self.Book_Got_Num = 0 # 已爬取网络小说的数量
        self.Book_Names = [] # 书名
        self.Author_Names = [] # 作者
        self.Book_Urls = [] # 书的网址

    # 翻页
    def get_next_page(self):
        self.Start_Url = self.Start_Url[:-1] + str(int(self.Start_Url[-1])+1)
        webdata = requests.get(self.Start_Url, headers=random.choice(self.headers))
        if '没有找到符合条件的书' in webdata.text:
            raise Exception("抛出一个异常")
        
    
    def parse_url(self,url):
        # 从指定网页url的内容读入到webdata中，以供分析使用
        webdata = requests.get(url, headers=random.choice(self.headers))
        # 通过xpath模块来分析网页内容
        selector = etree.HTML(webdata.text)
        return selector
    
    
    def check_name(self,s_name):
        """处理文件名非法字符的方法"""
        s_name = s_name.replace(' ','-')
        pattern = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'

        new_name = re.sub(pattern, "_", s_name)  # 替换为下划线
        return new_name

    # 获取书名
    def get_book_names(self,selector):
        self.Book_Names = selector.xpath('//*[@class="book-mid-info"]/h4/a/text()')
        
    # 获取作者名
    def get_author_names(self,selector):
        self.Author_Names = selector.xpath('//*[@class="author"]/a[1]/text()')
            
    # 获取书籍对应网址
    def get_book_urls(self,selector):
        book_nums = selector.xpath('//*[@class="book-mid-info"]/h4/a/@data-bid')
        self.Book_Urls = ['https://book.qidian.com/info/' + book_num + '#Catalog' for book_num in book_nums]
    
    # 获取章节名
    def get_chapters_names(self,selector):
        chapter_names = selector.xpath('//*[@class="cf"]/li/a/text()')
        return chapter_names
    
    # 获取章节网址
    def get_chapters_urls(self,selector):
        chapter_urls = selector.xpath('//*[@class="cf"]/li/a/@data-cid')
        chapter_urls = [chapter_url.replace('//','https://') for chapter_url in chapter_urls]
        return chapter_urls
    
    # 获取章节正文
    def get_chapter_contents(self,selector):
        chapter_contents = selector.xpath('//*[@class="read-content j_readContent"]/p/text()')
        return chapter_contents
        
    def save_to_txt(self,chapter_contents,book_name,author_name,chapter_name):
        # 章节要保存的路径名,为《书名》_作者名
        file_name = f'{self.Dirs_Save}《{book_name}》_{author_name}/'
        # 该路径不存在则创建
        if not os.path.exists(file_name):
            os.makedirs(file_name)
            
        # 章节存入的txt文件
        chapter_save = file_name + f'{chapter_name}.txt'
        f = open(chapter_save, 'w', encoding = 'utf-8')
        f.write('\n'.join(chapter_contents))   
        f.close()   
        
            
if __name__ == '__main__':   
    # 定义类的对象
    crawler = get_book_content()
    bknum_to_get = int(input('输入要爬取的小说数量：'))      

    while crawler.Book_Got_Num < bknum_to_get:
        # 查看该页可爬取的小说数量，并记录书名、作者、网址信息
        selector_page = crawler.parse_url(crawler.Start_Url)
        crawler.get_book_names(selector_page)
        crawler.get_book_urls(selector_page)
        crawler.get_author_names(selector_page)
        # 爬取该页小说
        for book_name,book_url,author_name in zip(crawler.Book_Names, crawler.Book_Urls, crawler.Author_Names):
            # 查看该小说可爬取的章节
            selector_book = crawler.parse_url(book_url)
            chapter_names = crawler.get_chapters_names(selector_book)
            chapters_urls = crawler.get_chapters_urls(selector_book)
            # 获取章节内容并保存
            for chapter_name,chapters_url in zip(chapter_names,chapters_urls):
                # 查看该小说可爬取的章节
                selector_chapter = crawler.parse_url(chapters_url)
                chapter_contents = crawler.get_chapter_contents(selector_chapter)
                crawler.save_to_txt(chapter_contents,book_name,author_name,chapter_name)
                print(f'已保存  {chapter_name}') 
                
            print(f'已保存《{book_name}》')
            crawler.Book_Got_Num += 1
            # 已爬取足够数量的小说，结束爬取
            if crawler.Book_Got_Num == bknum_to_get:
                print('爬取结束')
                break
                
        # 该页小说已爬取完成，爬取下一页  
        try:
            crawler.get_next_page()
        except:
            print(f'已爬取{crawler.Book_Got_Num}本小说，已无更多小说可供爬取')
            break    
            