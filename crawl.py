from bs4 import BeautifulSoup
import requests
import lxml.etree as et
import configparser
from os import path
import time
import re


# 请求头信息
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}
# 模式匹配
# pat_url = r"<a.*href=\"http://www.cankaoxiaoxi.com/(?!photo)(.*?).shtml[\"|\']."
pat_str = "<a.*href=\"(https?://.*?)[\"|\'].*"
pat_not_photo_str = r".*.cankaoxiaoxi.com/(?!photo).*"
pat = re.compile(pat_str)
pat_not_photo = re.compile(pat_not_photo_str)
# 链接前缀
# head_url = 'http://www.cankaoxiaoxi.com/'

# 广度搜索所用到的参数
# 深度字典
depth_dict = {}
# 临时存放的列表，作为待爬列表
temp_list = []
# 存放爬取到的所有url
url_list = []
encoding = 'utf-8'
doc_dir_path = r"data/news/"


def sleep(s=1):
    print(F'系统休眠{s}秒')
    time.sleep(s)

def get_html(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text, r.status_code
    except Exception as e:
        print(F"url = {url}出现故障\n错误信息为：")
        print(e)
        sleep(60)
        print("\n")
        print("故障休眠结束")
    return "", -1

def get_page_url(url):
    text, status = get_html(url)
    text = str(text)
    urls = re.findall(pat, text)
    # print(F"本次找到{len(urls)}条链接\n")
    # print(urls)
    # print("\n")
    return urls,status


def get_urls(depth=5):
    i = 1
    j = 1
    with open('urls_3.txt','w') as f:
        while (len(temp_list)>0 and i < 40000):
            sleep(3)
            # 从临时列表当中删除首元素
            url = temp_list.pop(0)
            # 添加到链接列表
            # url_list.append(url)
            if depth_dict[url] < depth:
                # 获取子页面url列表
                j += 1
                print(F"当前j={j},i={i}")
                if j%10 == 0:
                    print(F"----当前第{j:06}次请求网页,i={i}---\n")
                if j%2000 == 0:
                                print("\n开始休眠\n")
                                print(F"i = {i}, j={j}\n")
                                sleep(180)
                sub_list, status = get_page_url(url)
                if status != 200:
                    continue
                for u in sub_list:
                    if u not in depth_dict:
                        if re.findall(pat_not_photo,u) == []:
                            continue
                        depth_dict[u] = depth_dict[url] + 1
                        temp_list.append(u)
                        f.write(u)
                        f.write('\n')
                        i += 1
                        if i%1000 == 0:
                            print(F"\t当前第{i:06}条链接, j={j},此时temp_list的长度为{len(temp_list)}\n\n")
    print(F"------i={i}  j={j}  len(temp_list)={len(temp_list)}--------")


def crawl_one_page(url):
    status = 0
    try:
        text, status=get_html(url)
        soup = BeautifulSoup(text, "html")
        # print(soup)
        
        title = soup.find_all(class_="articleHead")[0].get_text()
        # print(F'\n\ntitle\n{title}')
        date = soup.find_all(class_="articleBody")[0].find_all(id="pubtime_baidu")[0].get_text()
        # print(F"\n\ndate\n{date}")

        text = soup.find_all(class_='articleText')[0].get_text()
        # print(F"\n\ntext\n{text}")

        return status, title, date, text
    except Exception as e:
        status = -1
        print(F"\n读取url:{url}时出现错误：\n{e}")
        return status, "", "", ""

def crawl(url, doc_dir_path, doc_encoding, i=1):
    status,title,date,text = crawl_one_page(url)
    # if status == 0:
    # print('not status!')
    doc = et.Element('doc')
    et.SubElement(doc, "id").text = F"{i}"
    et.SubElement(doc, "url").text = url
    et.SubElement(doc, "title").text = title
    et.SubElement(doc, "datetime").text = date
    et.SubElement(doc, "body").text = text
    tree = et.ElementTree(doc)
    # 这里文件名的format一定要注意与index.py里面的construct_posting_list对应
    tree.write(doc_dir_path + F"{i}.xml", encoding = doc_encoding, xml_declaration = True, pretty_print=True)
    return 0
    # else:
    #     return -1


if __name__ == '__main__':
    ''' 这部分代码已经调试好
    i=1
    p=path.join(path.dirname(path.abspath(__file__)), 'config.ini')
    config = configparser.ConfigParser()
    config.read(p, 'utf-8')
    crawl(get_pool(),config['DEFAULT']['doc_dir_path'], config['DEFAULT']['doc_encoding'])
    print("finish")
    '''
    # start_url = 'http://www.cankaoxiaoxi.com/'
    # depth_dict[start_url] = 0
    # temp_list.append(start_url)
    # get_urls(3)
    # 深度为1时共有359条
    # 深度为2时共有2200条
    # print(F"------------本次共找到{i}条链接,---------------")
    # print("finish")
    # for url in url_list:
    #     print("\t"*depth_dict[url],F"#{depth_dict[url]}:{url}")


    with open('urls_3_ckxx.txt','r',encoding=encoding) as f:
        url_list = f.readlines()
        base_len = len(url_list)
        start = 1718
        url_list = url_list[start:]
    # url_list = ['http://www.cankaoxiaoxi.com/china/20201223/2428113.shtml']
    num_of_urls = len(url_list)
    print(F'本次总共有{num_of_urls}条urls需要爬取')
    success = 0
    for i in range(start,num_of_urls):
        sleep(1)
        if crawl(url_list[i][:len(url_list[i])-1],doc_dir_path=doc_dir_path,doc_encoding=encoding,i=i) == 0:
            success += 1
        else:
            continue
        if i%101 == 0:
            print("101休眠")
            sleep(60)
            print(F"当前i={i},已经完成{i/num_of_urls*100:05.2f}%,剩下{num_of_urls-i}条,success={success}\n")
  





