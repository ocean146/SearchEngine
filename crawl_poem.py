from bs4 import BeautifulSoup
import requests
import lxml.etree as et
import time
import datetime as dt


base_id =103272
MAX_nums = 50000
base_url = r"https://www.gushimi.org/gushi/"
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}
encoding = 'utf-8'
doc_dir_path = r"data/poem/"
# doc_dir_path = r"c:/po/"

def cur_time():
    curr_time = dt.datetime.now()
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
        print("故障休眠结束")
    return "", -1

def crawl(url):
    try:
        text, status = get_html(url)
        soup = BeautifulSoup(text, 'html')
        # id url title datetime body
        # print(soup.find_all(class_='box_title'))
        title = soup.find_all(class_='box_title')[1].get_text()
        raw_message = soup.find_all(class_='old_h1')[0].get_text()
        datetime = raw_message[len(raw_message)-10:len(raw_message)] + " " + "00:00:00"
        body_writer = raw_message[:len(raw_message)-15]
        body_text = soup.find_all(class_='newstext')[0].get_text()
        body = body_writer + "。" + body_text
        return title, datetime, body
    except Exception as e:
        print(F"url = {url}出现故障\n错误信息为：\n")
        print(e)
        sleep(30)
        print("\n")
        print("故障休眠结束\n\n")
        return "","",""

def to_xml(id, url, title, datetime, body):
    doc = et.Element('doc')
    et.SubElement(doc, "id").text = F"{id}"
    et.SubElement(doc, "url").text = url
    et.SubElement(doc, "title").text = title
    et.SubElement(doc, "datetime").text = datetime
    et.SubElement(doc, "body").text = body
    tree = et.ElementTree(doc)
    # 这里文件名的format一定要注意与index.py里面的construct_posting_list对应
    tree.write(doc_dir_path + F"{id}.xml", encoding = encoding, xml_declaration = True, pretty_print=True)
    # print('doc wirte finish')
    return 0

def main(start=1, end=MAX_nums):
    delta = end - start
    for i in range(start,end):
        # print(F"{i}\n")
        url = base_url + str(i) + '.html'
        # print(url)
        t, d, b = crawl(url)
        # print(F"{t}\n{d}\n{b}\n")
        id = str(base_id + i)
        to_xml(id, url, t, d, b)
        if i%100 == 0:
            print(F'\n已完成{i}条，总共{delta}条')
    print('finish')

if __name__ == '__main__':
    # print("i\t\ttitle\t\tdatetime\tbody")
    # for i in range(0,6):
    #     url = base_url+ str(i) +'.html'
    # # url = 'https://www.gushimi.org/gushi/1.html'
    # title, datetime, body = crawl(url)
    # print(F"{i}\t\t{title}\t\t{datetime}\t{body}\n")
    main(35686)
    with open('log_info.txt', 'w') as f:
        print('\n-------------')
        f.write(cur_time())
        f.write("\nfinish\n-------------")
    