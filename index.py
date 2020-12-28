from os import listdir, path
import lxml.etree as et
import jieba
import sqlite3


stop_words_dir = path.join(path.dirname(path.abspath(__file__)), r'data\stop_words.txt')
encoding = 'utf-8'
doc_dir_path = r"data/news/"
db_path = r'data/ir.db'

class Doc:
    docid = 0
    date_time = ''
    tf = 0  # 词项频率
    ld = 0  # 文档长度
    def __init__(self, docid, date_time, tf, ld):
        self.docid = docid
        self.date_time = date_time
        self.tf = tf
        self.ld = ld

    def __repr__(self):
        # 展示函数
        return (str(self.docid) + "\t" + self.date_time +'\t' + str(self.tf) + 't' + str(self.ld))
    
    def __str__(self):
        return (str(self.docid) + "\t" + self.date_time + '\t' + str(self.tf) + '\t' + str(self.ld))

class IndexModule:

    def __init__(self):
        f = open(stop_words_dir, encoding = encoding)
        words = f.read()
        self.stop_words = set(words.split('\n'))
        self.stop_words = set()
        self.postings_lists = {}  # 倒排记录表，记录出现词项的文章

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError as Ve:
            return False

    def clean_list(self, seg_list):
        # 该函数的作用是，去掉停用词，将剩下的词放入cleaned_dict当中
        cleaned_dict = {}
        n = 0  # 文本长度
        for i in seg_list:
            i = i.strip().lower()  # strip方法移除字符串头尾指定字符
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                # 非空          非数字                非停止词
                n += 1  # 词数+1
                if i in cleaned_dict:  # 若已经在词典当中
                    cleaned_dict[i] = cleaned_dict[i] + 1 # 该词词频数+1
                else:
                    cleaned_dict[i] = 1  # 创建新词
        return n, cleaned_dict

    def write_postings_to_db(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute('''DROP TABLE IF EXISTS postings''')  # 如果数据库中存在posting表，就把它从数据库中drop掉
                                                        # drop是删除数据结构的意思
        c.execute('''CREATE TABLE postings
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''') 
                     #      主键term     整型 df    文本 docs 

        for key, value in self.postings_lists.items():
            # postings_lists结构：{词项：[df,[doc1,doc2,...]],...}
            doc_list = '\n'.join(map(str,value[1]))
            t = (key, value[0], doc_list)
            c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

        conn.commit()
        conn.close()

    def construct_postings_lists(self):
        # files = listdir(doc_dir_path)
        # files2 = listdir(r"data/news_sina/")
        files = listdir(r"data/poem/")
        AVG_L = 0
        for i in files:
            root = et.parse(doc_dir_path + i).getroot()  # 获取根元素
            title = ""
            title = root.find('title').text
            body = root.find('body').text
            docid = int(root.find('id').text)
            date_time = root.find('datetime').text
            if title == None:
                continue
            seg_list = jieba.lcut(title + '。' + body, cut_all=False)  # jieba分词返回一个列表
            
            ld, cleaned_dict = self.clean_list(seg_list)

            AVG_L = AVG_L +ld

            for key, value in cleaned_dict.items():
                # cleaned_dict数据结构为： （词项：频数）
                d = Doc(docid, date_time, value, ld)
                if key in self.postings_lists:
                    self.postings_lists[key][0] += 1  # df文档频率加1
                    self.postings_lists[key][1].append(d)
                else:
                    self.postings_lists[key] = [1, [d]]  # 新建索引
        
        AVG_L = AVG_L / len(files)
        with open('info.txt','w') as f:
            f.write(F"N={len(files)}\n")
            f.write(F'avg_l={AVG_L}\n')
        self.write_postings_to_db(db_path)
    # postings_lists结构：{词项：[df,[doc1,doc2,...]],...}
        

if __name__ == '__main__':
    im = IndexModule()
    im.construct_postings_lists()


