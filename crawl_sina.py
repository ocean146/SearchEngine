from bs4 import BeautifulSoup
import requests
import lxml.etree as et
import time
import re
import datetime


base_url = r"https://news.sina.com.cn/"
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}

pat_str = "<a.*href=\"(https?://.*?)[\"|\'].*"
pat = re.compile(pat_str)

encoding = 'utf-8'
doc_dir_path = r"data/news_sina/"
# 广度搜索所用到的参数
# 深度字典
depth_dict = {}
# 临时存放的列表，作为待爬列表
temp_list = []
# 存放爬取到的所有url
url_list = []

def cur_time():
    curr_time = datetime.datetime.now()
    return curr_time.strftime("%m/%d %H:%M:%S")


def sleep(s=0.1):
    print(F"休眠{s}秒\n")
    time.sleep(s)

def get_html(url):
    try:
        r = requests.get(url, headers=headers)
        r.encoding='utf-8'
        if r.status_code == 200:
            return r.text, r.status_code
    except Exception as e:
        print(F"url = {url}出现故障\n错误信息为：\n")
        print(e)
        sleep(60)
        print("\n")
        print("故障休眠结束\n\n")
    return "", -1

def crawl(url):
    text, status = get_html(url)
    soup = BeautifulSoup(text, 'html')
    # id url title datetime body
    # print(soup.find_all(class_='box_title'))
    if len(soup.find_all(id='article'))==0:
        body=""
    else:
        body=soup.find_all(id='article')[0].get_text()
    if len(soup.find_all(class_='main-title'))==0:
        title=""
    else:
        title=soup.find_all(class_='main-title')[0].get_text()
    datetime_=text[37:56]
    try:
        if datetime_.strip()[0] != '2':
            datetime_ = '2' + datetime_.strip()
    except:
        print('date error\n')
    return title, datetime_, body

def get_page_url(url):
    text, status = get_html(url)
    text = str(text)
    urls = re.findall(pat, text)
    # print(F"本次找到{len(urls)}条链接\n")
    # print(urls)
    # print("\n")
    return urls,status

def get_urls(depth=5):
    i = 1  # 已经捕获的链接数
    j = 1  # 已经请求网页的次数
    temp_list.append(base_url)
    depth_dict[base_url] = 0
    with open('urls_sina.txt','w') as f:
        while (len(temp_list)>0 and i < 90000):
            # sleep(3)
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
                # if j%2000 == 0:
                #                 print("\n开始休眠\n")
                #                 print(F"i = {i}, j={j}\n")
                #                 sleep(180)
                sub_list, status = get_page_url(url)
                if status != 200:
                    continue
                for u in sub_list:
                    if u not in depth_dict :
                        if (not u.endswith('html')) and depth_dict[url]<2:
                            continue
                        depth_dict[u] = depth_dict[url] + 1
                        temp_list.append(u)
                        try:
                            f.write(u)
                            f.write('\n')
                            i += 1
                        except Exception as e:
                            print('----写错误-----\n')
                            print(e)
                            print('\n')
                            continue
                        if i%1000 == 0:
                            print(F"\t当前第{i:06}条链接, j={j},此时temp_list的长度为{len(temp_list)}\n\n")
    print(F"------i={i}  j={j}  len(temp_list)={len(temp_list)}--------")

def to_xml(id, url, title, datetime, body):
    try:
        doc = et.Element('doc')
        et.SubElement(doc, "id").text = F"{id}"
        et.SubElement(doc, "url").text = url
        et.SubElement(doc, "title").text = title
        et.SubElement(doc, "datetime").text = datetime
        et.SubElement(doc, "body").text = body
        tree = et.ElementTree(doc)
        # 这里文件名的format一定要注意与index.py里面的construct_posting_list对应
        tree.write(doc_dir_path + F"{id}.xml", encoding = encoding, xml_declaration = True, pretty_print=True)
        return 0
    except:
        return -1

if __name__ == '__main__':
    last_ckxx_id=13279
    last_id = 18689
    # get_urls(5)
    # print('----------urls获取完成-----------')
    with open('urls_sina.txt','r',encoding="gbk") as f:
        urls_list = f.readlines()[last_id-last_ckxx_id:]
        base_len = len(urls_list)
        j = 0
        for i in range(len(urls_list)):
            if not urls_list[i].strip().endswith('shtml'):
                continue
            t, d, b =crawl(urls_list[i].rstrip())
            to_xml(i+last_id, urls_list[i], t, d, b)
            j += 1
            if i%100 == 0:
                print(F"\n当前有效信息条数：{i} 总共条数:{base_len}\n")
    print('finnal finish!')
    print(cur_time())


        # start = 0
        # url_list = url_list[start:]
    # print(F'本次总共有{num_of_urls}条urls需要爬取')
    # success = 0
    # for i in range(start,num_of_urls):
    #     sleep(1)
    #     if crawl(url_list[i],doc_dir_path=doc_dir_path,doc_encoding=encoding,i=i) == 0:
    #         success += 1
    #     else:
    #         continue
    #     if i%101 == 0:
    #         print("101休眠")
    #         sleep(60)
    #         print(F"当前i={i},已经完成{i/num_of_urls*100:05.2f}%,剩下{num_of_urls-i}条,success={success}\n")