from flask import Flask, request
from flask import jsonify
from bs4 import BeautifulSoup
import requests
import urllib.request
app = Flask(__name__)

# 用于储存20条新闻的地址
adress=[]
@app.route("/")
def newHello():
    return "{'HH':'V11V'}"

# 测试的爬虫
@app.route('/title/<number>')
def catchCtbu(number):
    newsLink=['jjgsd.htm','zhxw.htm','ggxx.htm','jxky.htm','xtdt.htm','zsjy.htm','mtgz.htm']
    urlNumber=int(number)
    # print(urlNumber)
    url='http://news2014.ctbu.edu.cn/'+newsLink[urlNumber]
    # print(url)
    response = requests.get(url)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, 'lxml')
    link_ul = bs.select(".global_tx_list4")
    link_div = link_ul[0].find_all('div')
    node = link_div[0].find_all('ul')
    link = node[0].find_all('li')
    storageDate = []
    storageTitle = []
    global adress
    adress=[]
    for i in link:
        link_span = i.find_all('span')
        storageDate.append(link_span[0].text)
        link_a = i.find_all('a')
        storageTitle.append(link_a[1].text)
        for j in link_a:
            if (j.get('target') == "_blank"):
                if str(j.get('href'))[:4] == 'info':
                    total = 'http://news2014.ctbu.edu.cn/' + j.get('href')
                    adress.append(total)
    return jsonify({'storageTitle':storageTitle,'storageDate':storageDate})

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0')
#
#
#
#
#用于新闻的bodyText
@app.route('/showdetail/<index>')
def showDetailNews(index):
    number = int(index)
    global adress
    url = adress[number]
    response1 = requests.get(url)
    print(url)
    response1.encoding = 'utf-8'
    bs1 = BeautifulSoup(response1.text, 'lxml')
    node1 = bs1.select(".article_body")
    link1 = node1[0].find_all("span")
    body_len = len(link1)
    body_text = []
    for i in range(body_len):
        total=link1[i].text
        body_text.append(total)
    return jsonify({'bodyText': body_text})