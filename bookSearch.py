from flask import Flask
from flask import jsonify
from lxml import etree
from bs4 import BeautifulSoup
import requests
import re
# 用于编码
from urllib import parse


app = Flask(__name__)
theSameUrl=""
s = requests.session()

# 第一次搜索
@app.route("/search/<keyWord>/<model>/<type1>/<field>/<disk1>")
def bs(keyWord,model,field,disk1,type1):
    # 搜索的字眼
    keyword = screenText=keyWord
    # 搜索的模式如部分搜索/包含搜索
    searchModel = model
    # 搜索类型如图书或者期刊
    if(type1=='all'):
        name=""
    else:
        name = type1
    # 搜索的范围如作者/题名
    searchfield =field
    # 是否有光盘
    if(disk1=='no'):
        disk=""
    else:
        disk=disk1
    data1 = {
        'tag': 'search',
        'subtag': 'searchresult',
        'gcbook': 'yes',
        'viewtype': '',
        'flword': keyword,
        'searchType': 'oneSearch',
        'corename': name,
        'title': '',
        'searchFieldType': 'text',
        'aliasname': '全部馆藏',
        'q': screenText,
        'searchModel': searchModel,
        'field': searchfield,
        'disk': disk
    }
    url = "http://libopac.ctbu.edu.cn/opac/search"
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
    }
   # 发起post请求
    response = s.post(url, data1, headers1)
    # 网页源码是utf-8要先解码
    content = response.content.decode('utf-8')
    bs = BeautifulSoup(content, 'lxml')

    # 这是取页数的节点
    node1 = bs.select("div .search_page")
    try:
        nodeRecord = node1[0].find_all("span")
        record = nodeRecord[0].text
        numberRecord = re.search('\d+', record)
        number = int(numberRecord.group())
        print(number)
    except:
        print("failed")
        # return  jsonify({'searchResult': [], 'data1': 1,'theSame':'' ,'pages':1})
    if (number >10):
        link_page_a = node1[0].find_all('a')
        # link_page_a
        k = 0
        len_a = len(link_page_a)
        for each in link_page_a:
            k = k + 1
            if (k == len_a):
                str2 = each.get('href')
        ret = re.search(".*pager.offset=(\d+)", str2)
        maxPages = ret.group(1)

        # 总共的页数
        pages = int(maxPages) / 10
        pages=pages+1
        print(pages)
        same = len(str2) - len(maxPages)
        # 取url相同的部分
        theSame = 'http://libopac.ctbu.edu.cn/' + str2[0:same]
        num = 0
        pagesUrl = theSame + '%d' % num
        response = requests.get(pagesUrl)
        response.encoding = "utf-8"
        bs2 = BeautifulSoup(response.text, 'lxml')
        bs = bs2
    else:
        pages = 1
        theSame = "Null"
    # 抓取class=jp-searchList下的源码
    node = bs.select(".jp-searchList")
    # 储存所有的li
    link = node[0].find_all("li")
    # 用于储存所有的搜索结果
    total = []
    # 用于记录
    len_li = len(link)
    for i in range(len_li):
        part = []
        link_title = link[i].find_all('a')
        part.append(link_title[0].text)
        link_div = link[i].find_all('div')
        link_p = link_div[0].find_all('p')
        len_p = len(link_p)
        k = 0
        for each in link_p:
            k = k + 1
            j = k - 1
            if (j + 1 == len_p):
                link_button = link_p[j].find_all('button')
                bookNumber = link_button[0].get('id')
                # print(bookNumber)
                bookNumberCode = parse.quote(bookNumber)
                bookNumberUrl = 'http://libopac.ctbu.edu.cn/opac/book/getBookState/' + bookNumber + '/' + bookNumberCode
                responseNumber = requests.get(bookNumberUrl)
                responseNumber.encoding = 'utf-8'
                numberBS = BeautifulSoup(responseNumber.text, 'lxml')
                numberNode = numberBS.select('p')
                number = numberNode[0].text
                ret = re.match('([0-9]*)/([0-9]*)', number)
                totalNumber = ret.group(1)
                lent = ret.group(2)
                collect = '馆藏：' + str(totalNumber)
                lentOthers = '可外借：' + str(lent)
                part.append(collect)
                part.append(lentOthers)
            if (k != len_p):
                part.append(each.text)
        total.append(part)
    global   theSameUrl
    theSameUrl=theSame
    print(theSame)
    return jsonify({'searchResult': total, 'data1': 1,'theSame':theSame ,'pages':pages})

# 改变页数
@app.route('/changePage/<page>')
def ChangePage(page):
    global theSameUrl
    theSame=theSameUrl
    num = int(page)*10
    pagesUrl = theSame + '%d' % num
    response = requests.get(pagesUrl)
    response.encoding = "utf-8"
    bs = BeautifulSoup(response.text, 'lxml')
    # 抓取class=jp-searchList下的源码
    node = bs.select(".jp-searchList")
    # 储存所有的li
    link = node[0].find_all("li")
    # 用于储存所有的搜索结果
    total = []
    # 用于记录
    len_li = len(link)
    for i in range(len_li):
        part = []
        link_title = link[i].find_all('a')
        part.append(link_title[0].text)
        link_div = link[i].find_all('div')
        link_p = link_div[0].find_all('p')
        len_p = len(link_p)
        k = 0
        for each in link_p:
            k = k + 1
            j = k - 1
            if (j + 1 == len_p):
                link_button = link_p[j].find_all('button')
                bookNumber = link_button[0].get('id')
                bookNumberCode = parse.quote(bookNumber)
                bookNumberUrl = 'http://libopac.ctbu.edu.cn/opac/book/getBookState/' + bookNumber + '/' + bookNumberCode
                responseNumber = requests.get(bookNumberUrl)
                responseNumber.encoding = 'utf-8'
                numberBS = BeautifulSoup(responseNumber.text, 'lxml')
                numberNode = numberBS.select('p')
                number = numberNode[0].text
                ret = re.match('([0-9]*)/([0-9]*)', number)
                totalNumber = ret.group(1)
                lent = ret.group(2)
                collect = '馆藏：' + str(totalNumber)
                lentOthers = '可外借：' + str(lent)
                part.append(collect)
                part.append(lentOthers)
            if (k != len_p):
                part.append(each.text)
        total.append(part)
    return jsonify({'searchResult': total,'data1':2})


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0')