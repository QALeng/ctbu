#-*-coding:utf-8-*-
import os

# 用于对名字进行编码
import re
from urllib import parse


from imp import reload
from skimage import io

from lxml import etree

import sys
from bs4 import BeautifulSoup

from flask import Flask, request
from flask import jsonify

import requests
app = Flask(__name__)
s = requests.session()

#初始参数，自己输入的学号，密码。
@app.route('/login/<total>/<password>')
def login(total,password):
    global  studentNumber
    studentNumber =total[4:len(total)]
    code=total[0:4]
    password=password
    print(password)
    print(code)
    url = "http://jwsys.ctbu.edu.cn/Default2.aspx"
    global  s
    response = s.get(url)
    selector = etree.HTML(response.content)
    __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "txtUserName": studentNumber,
        "TextBox2": password,
        "txtSecretCode": code,
        "Button1": "",
    }
    # 提交表头，里面的参数是电脑各浏览器的信息。模拟成是浏览器去访问网页。
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
    }
    # 登陆教务系统
    response = s.post(url, data=data, headers=headers)
    print("成功进入")
    # 得到登录信息，个人感觉有点多余。
    def getInfor(response, xpath):
        content = response.content.decode('gb2312')  # 网页源码是gb2312要先解码
        selector = etree.HTML(content)
        infor = selector.xpath(xpath)[0]
        return infor

    # 获取学生基本信息
    text = getInfor(response, '//*[@id="xhxm"]/text()')
    text = text.replace(" ", "")
    print(text)
    global studentName
    studentName = re.sub('同学', '', text)
    return jsonify({'login':1})

@app.route('/code')
def code():
    url = "http://jwsys.ctbu.edu.cn/Default2.aspx"
    response = s.get(url)
    imgUrl = "http://jwsys.ctbu.edu.cn/CheckCode.aspx"
    imgresponse = s.get(imgUrl, stream=True)
    print(s.cookies)
    image = imgresponse.content
    DstDir = os.getcwd() + "\static\image\\"
    # DstDir = "C:\\Users\\Administrator\\Desktop\\app\\pages\\image\\"
    print("保存验证码到：" + DstDir + "code.jpg" + "\n")
    try:
        with open(DstDir + "code.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")
    finally:
        jpg.close
    return jsonify({"Ture":1})
 # return jsonify({'searchResult': total,'data1':1222}) 传两个参数
@app.route("/")
def newHello():
    return "{'HH':'V11V'}"

@app.route("/score/<year>/<term>")
def lookScore(year,term):
    global studentNumber
    ddlxn = year
    ddlxq = term
    _eventtarget = ""
    _eventagument = ""
    _viewstate = "dDwxMDk5MDkzODA4O3Q8cDxsPHRqcXI7PjtsPDE7Pj47bDxpPDE+Oz47bDx0PDtsPGk8MT47aTw3PjtpPDk+Oz47bDx0PHQ8O3Q8aTwxOT47QDzlhajpg6g7MjAwMS0yMDAyOzIwMDItMjAwMzsyMDAzLTIwMDQ7MjAwNC0yMDA1OzIwMDUtMjAwNjsyMDA2LTIwMDc7MjAwNy0yMDA4OzIwMDgtMjAwOTsyMDA5LTIwMTA7MjAxMC0yMDExOzIwMTEtMjAxMjsyMDEyLTIwMTM7MjAxMy0yMDE0OzIwMTQtMjAxNTsyMDE1LTIwMTY7MjAxNi0yMDE3OzIwMTctMjAxODsyMDE4LTIwMTk7PjtAPOWFqOmDqDsyMDAxLTIwMDI7MjAwMi0yMDAzOzIwMDMtMjAwNDsyMDA0LTIwMDU7MjAwNS0yMDA2OzIwMDYtMjAwNzsyMDA3LTIwMDg7MjAwOC0yMDA5OzIwMDktMjAxMDsyMDEwLTIwMTE7MjAxMS0yMDEyOzIwMTItMjAxMzsyMDEzLTIwMTQ7MjAxNC0yMDE1OzIwMTUtMjAxNjsyMDE2LTIwMTc7MjAxNy0yMDE4OzIwMTgtMjAxOTs+Pjs+Ozs+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47PjtsPHQ8O2w8aTwwPjs+O2w8dDxwPGw8aW5uZXJodG1sOz47bDwyMDE3LTIwMTjlrablubTnrKwx5a2m5pyf5a2m5Lmg5oiQ57upOz4+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47PjtsPHQ8cDxsPGlubmVyaHRtbDs+O2w85a2m5Y+377yaMjAxNzEzNzEzMjs+Pjs7Pjt0PHA8bDxpbm5lcmh0bWw7PjtsPOWnk+WQje+8muenpuWumuatpjs+Pjs7Pjt0PHA8bDxpbm5lcmh0bWw7PjtsPOWtpumZou+8muiuoeeul+acuuenkeWtpuS4juS/oeaBr+W3peeoi+WtpumZojs+Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjs+O2w8dDxwPGw8aW5uZXJodG1sOz47bDzkuJPkuJrvvJrnianogZTnvZHlt6XnqIs7Pj47Oz47dDxwPGw8aW5uZXJodG1sOz47bDzooYzmlL/nj63vvJoxN+eJqeiBlOe9kTs+Pjs7Pjs+Pjs+Pjt0PEAwPHA8cDxsPFBhZ2VDb3VudDtfIUl0ZW1Db3VudDtfIURhdGFTb3VyY2VJdGVtQ291bnQ7RGF0YUtleXM7PjtsPGk8MT47aTwxMT47aTwxMT47bDw+Oz4+Oz47QDA8Ozs7Ozs7Ozs7Ozs7Ozs7OztAMDxwPGw8VmlzaWJsZTs+O2w8bzxmPjs+Pjs7Ozs+Ozs7Ozs+Ozs7Ozs7Ozs7PjtsPGk8MD47PjtsPHQ8O2w8aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47PjtsPHQ8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1PjtpPDE2PjtpPDE3PjtpPDE4PjtpPDE5PjtpPDIwPjtpPDIxPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDwoMjAxNy0yMDE4LTEpLTYxMDEzMDctMTk5NzAyMS0yOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTIwMTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDYxMDEzMDc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOmrmOetieaVsOWtpkHihaA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWkp+exu+WfuuehgOivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NS4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw5NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8ODA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDgzOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzmlbDlrabkuI7nu5/orqHlrabpmaI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMzA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47aTwxNT47aTwxNj47aTwxNz47aTwxOD47aTwxOT47aTwyMD47aTwyMT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTctMjAxOC0xKS02MTMyMzA1LTIwMTAwMzQtMTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MjAxNy0yMDE4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw2MTMyMzA1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDznianogZTnvZHlt6XnqIvlr7zorro7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWkp+exu+WfuuehgOivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mi4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw4NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NzU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDc4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzorqHnrpfmnLrnp5HlrabkuI7kv6Hmga/lt6XnqIvlrabpmaI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIuODA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47aTwxNT47aTwxNj47aTwxNz47aTwxOD47aTwxOT47aTwyMD47aTwyMT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTctMjAxOC0xKS02MTAxMzA2LTQxMFdQMDQtMTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MjAxNy0yMDE4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw2MTAxMzA2Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDznur/mgKfku6PmlbBCOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlpKfnsbvln7rnoYDor747Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8OTE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDk4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw5Nzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85pWw5a2m5LiO57uf6K6h5a2m6ZmiOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw0LjcwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+O2k8MTY+O2k8MTc+O2k8MTg+O2k8MTk+O2k8MjA+O2k8MjE+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPCgyMDE3LTIwMTgtMSktNjAwMDYwMy0yMDEzMDIyLTY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMTctMjAxODs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NjAwMDYwMzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85Yab6K6t77yI5ZCr5Yab5LqL55CG6K6677yJOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlrp7ot7Xnjq/oioLor747Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8OTM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDkyOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw5Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85YWa5aeU5a2m55Sf5bel5L2c6YOo44CB5q2m6KOF6YOo44CB5a2m55Sf5aSEOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw0LjMwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+O2k8MTY+O2k8MTc+O2k8MTg+O2k8MTk+O2k8MjA+O2k8MjE+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPCgyMDE3LTIwMTgtMSktNjE1MzEwMi0yMDAyMDkxLTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMTctMjAxODs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NjE1MzEwMjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85aSn5a2m6Iux6K+tQuKFoDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86YCa6K+G5b+F5L+u6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1LjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDg5Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw0NDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDY3Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlpJbor63lrabpmaI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDEuNzA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47aTwxNT47aTwxNj47aTwxNz47aTwxOD47aTwxOT47aTwyMD47aTwyMT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTctMjAxOC0xKS02MDAwMTAxLTIwMDMwMjEtNTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MjAxNy0yMDE4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw2MDAwMTAxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlv4PnkIblgaXlurc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOmAmuivhuW/heS/ruivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MC41Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw5MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8ODc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDg4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlhZrlp5TlrabnlJ/lt6XkvZzpg6jjgIHmraboo4Xpg6jjgIHlrabnlJ/lpIQ7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuODA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47aTwxNT47aTwxNj47aTwxNz47aTwxOD47aTwxOT47aTwyMD47aTwyMT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTctMjAxOC0xKS02MTY1MTA3LTIwMTQwMjgtMzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MjAxNy0yMDE4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw2MTY1MTA3Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlvaLlir/kuI7mlL/nrZZJOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzpgJror4blv4Xkv67or747Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDAuNTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8OTc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDc0Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw4MTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86ams5YWL5oCd5Li75LmJ5a2m6ZmiOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzLjEwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+O2k8MTY+O2k8MTc+O2k8MTg+O2k8MTk+O2k8MjA+O2k8MjE+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPCgyMDE3LTIwMTgtMSktdHl4bWswNS0yMDAxMDQ2LTExOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTIwMTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPHR5eG1rMDU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOe+veavm+eQgzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86YCa6K+G5b+F5L+u6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDk1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw4Mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8ODc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS9k+iCsuWtpumZojs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My43MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1PjtpPDE2PjtpPDE3PjtpPDE4PjtpPDE5PjtpPDIwPjtpPDIxPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDwoMjAxNy0yMDE4LTEpLTYxNjMxMDEtMTk4NjAzNy01Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTIwMTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDYxNjMxMDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS4reWbvei/keeOsOS7o+WPsue6suimgTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86YCa6K+G5b+F5L+u6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDg1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw3ODs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8ODI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOmprOWFi+aAneS4u+S5ieWtpumZojs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4yMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1PjtpPDE2PjtpPDE3PjtpPDE4PjtpPDE5PjtpPDIwPjtpPDIxPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDwoMjAxNy0yMDE4LTEpLTYxMzI0MjMtMTk5NjA3Ny0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTIwMTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDYxMzI0MjM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOmrmOe6p+eoi+W6j+iuvuiuoSAoQ+ivreiogClCIDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85LiT5Lia5qC45b+D6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDk4Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw4NDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8OTA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOiuoeeul+acuuenkeWtpuS4juS/oeaBr+W3peeoi+WtpumZojs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1PjtpPDE2PjtpPDE3PjtpPDE4PjtpPDE5PjtpPDIwPjtpPDIxPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDwoMjAxNy0yMDE4LTEpLTYxMzI0MjQtMTk5NjA3Ny0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTIwMTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDYxMzI0MjQ7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOmrmOe6p+eoi+W6j+iuvuiuoShD6K+t6KiAKULlrp7pqow7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS4k+S4muaguOW/g+ivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MS4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw5NDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8OTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDkzOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzorqHnrpfmnLrnp5HlrabkuI7kv6Hmga/lt6XnqIvlrabpmaI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDQuMzA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjs+Pjs+Pjs+Pjs+Pjs+wk0DHm2lmaWipwPF43sdrFV7A+Q="
    btnCx = "(unable to decode value)"
    scoreData = {
        "__EVENTTARGET": _eventtarget,
        "__EVENTARGUMENT": _eventagument,
        "__VIEWSTATE": _viewstate,
        'ddlxn': ddlxn,
        'ddlxq': ddlxq,
        'btnCx': btnCx
    }
    # 这个变量跟随姓名而变
    # name="%C7%D8%B6%A8%CE%E4"
    # name = "%BF%C2%D4%F6%D1%E0"
    global studentName
    name = parse.quote(studentName)
    scoreUrl = "http://jwsys.ctbu.edu.cn/xscjcx_dq.aspx?xh="+studentNumber+"&xm="+name+"&gnmkdm=N121707"
    referer="http://jwsys.ctbu.edu.cn/xs_main.aspx?xh="+studentNumber
    scoreHeaders = {
        "Referer":referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
    }
    # 这里有一个很诡异的错误
    global s
    response = s.post(scoreUrl, scoreData, headers=scoreHeaders)
    html = response.content.decode("gb2312", "ignore")
    bs = BeautifulSoup(html, 'lxml')
    node = bs.select(".datelist")
    link_tr = node[0].find_all('tr')
    link_td = link_tr[0].find_all('td')
    len_tr = len(link_tr)
    len_td = len(link_td)
    score = []
    for j in range(len_tr):
        if (j == 0):
            continue
        course = []
        link_td = link_tr[j].find_all('td')
        # 3 4 6 7 8 10 13
        for i in range(len_td):
            if (i == 3 or i == 4 or i == 6 or i == 7 or i == 8 or i == 10):
                course.append(link_td[i].text)
        score.append(course)
    return jsonify({'score':score})

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0')
