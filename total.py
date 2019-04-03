#-*-coding:utf-8-*-
from flask import Flask, request
import os
import pymysql
from lxml import etree
from bs4 import BeautifulSoup
from flask import jsonify
import requests
import re
# 用于编码
from urllib import parse


app = Flask(__name__)

name=""

s = requests.session()

@app.route('/')
def hello_world():
    return '<h1 style="font-size: 400%;" align="center">Hello World!<h1>'

@app.route('/login/<total>/<password>')
def login(total,password):
    success="fales"
    global studentNumber
    studentnumber =total[4:len(total)]
    studentNumber=studentnumber
    code=total[0:4]
    password=password
    print(password)
    print(code)
    # 访问教务系统,前面分析过了，提交数据时要用这个值。先得到__VIEWSTATE的值。
    url = "http://jwsys.ctbu.edu.cn/Default2.aspx"
    response = s.get(url)
    selector = etree.HTML(response.content)
    __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "txtUserName": studentnumber,
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
    bs = BeautifulSoup(response.text, 'lxml')
    node = bs.select("#xhxm")
    node[0].text
    xm = node[0].text
    name=xm[:-2]
    if(xm[-2:]=="同学"):
        success="ture"
    print(success)
    global studentName
    studentName=name
    print("欢迎！"+xm)
     # 得到登录信息，个人感觉有点多余。
    return jsonify({"name":name,"success":success})



@app.route('/code')
def code():
    url = "http://jwsys.ctbu.edu.cn/Default2.aspx"
    response = s.get(url)
    imgUrl = "http://jwsys.ctbu.edu.cn/CheckCode.aspx"
    imgresponse = s.get(imgUrl, stream=True)
    print(s.cookies)
    image = imgresponse.content
    DstDir = os.getcwd() + "\static\image\\"
    # DstDir = os.getcwd() + "\static\image\\"
    print(DstDir)
    print("保存验证码到：" + DstDir + "code2.jpg" + "\n")
    try:
        with open(DstDir + "code2.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")
    finally:
        jpg.close
    return jsonify({"Ture":1})

@app.route('/libraryCode')
def librarycode():
    for i in range(100):
        url = "http://libopac.ctbu.edu.cn/textCode/"
        headers = {
            "Referer": "http://libopac.ctbu.edu.cn/opac/login?locale=zh_CN",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
        response = s.post(url, headers=headers)
        bs = BeautifulSoup(response.text, 'lxml')
        node = bs.select(".vc-img1")
        imageUrl = node[0].get("src")
        if(imageUrl[-1:]=="="):
            continue
        return imageUrl


@app.route('/kb')
def kb():
    kb1_2 = []
    kb3_4 = []
    kb5_6 = []
    kb7_8 = []
    kb9_10 = []
    kburl = "http://jwsys.ctbu.edu.cn/xskbcx.aspx?xh="+studentNumber+"&xm="+studentName+"&gnmkdm=N121603"
    headers = {
    "Referer":"http://jwsys.ctbu.edu.cn/xs_main.aspx?xh=2017137137",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
     }
    response = s.get(kburl,headers=headers)
    bs=BeautifulSoup(response.text,'lxml')
    node = bs.select(".blacktab")
    link = node[0].find_all("tr")
    print(link[2].text)
    linkc1_2=link[2].find_all("td")
    linkc3_4=link[4].find_all("td")
    linkc5_6=link[6].find_all("td")
    linkc7_8=link[8].find_all("td")
    linkc9_10=link[10].find_all("td")
    print(linkc1_2)
    len1_2=len(linkc1_2)
    len3_4=len(linkc3_4)
    def sb(a,b):
        for i in range(len(a)):
            if (a[i].text=="上午"or a[i].text=="第1节"or a[i].text=="下午"or a[i].text=="第3节"or a[i].text=="第5节"or a[i].text=="第7节"or a[i].text=="第9节"or a[i].text=="晚上"):
                continue
            elif(a[i].text=="\xa0"):
                b.append("")
            else:
                b.append(a[i].text)
    sb(linkc1_2,kb1_2)
    sb(linkc3_4,kb3_4)
    sb(linkc5_6,kb5_6)
    sb(linkc7_8,kb7_8)
    sb(linkc9_10,kb9_10)

    return jsonify({"kb1_2":kb1_2,"kb3_4":kb3_4,"kb5_6":kb5_6,"kb7_8":kb7_8,"kb9_10":kb9_10})

@app.route('/libraryLogin/<username>/<password>/<validCode>')
def libraryLogin(username,password,validCode):
    text:[]
    loginType = "barCode"
    headers = {
        "Referer": "http://libopac.ctbu.edu.cn/opac/login?locale=zh_CN",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    data = {
        "username": username,
        "password": password,
        "loginType": loginType,
        "validCode": validCode
    }
    url = "http://libopac.ctbu.edu.cn/pages/include/checklogin.jsp"
    response = s.post(url, data=data, headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')
    text=bs.text
    print(data)
    print(text)
    return jsonify({"text":text})

@app.route('/library')
def library():
    lenHistory=0
    textHistory=[]
    renewNumber = []
    titleHistory=[]
    barCodeHistory=[]
    timeHistory=[]
    title = []
    barCode = []
    loanTime = []
    returnTime = []
    operation=[]
    fine = []
    response = s.get("http://libopac.ctbu.edu.cn/opac/mylibrary")
    bs = BeautifulSoup(response.text, 'lxml')
    node = bs.select(".cell_binggrzx")
    link = node[0].find_all("tr")
    for i in range(len(link) - 1):
        linkTd = link[i + 1].find_all("td")
        title.append(linkTd[1].text)
        barCode.append(linkTd[2].text)
        renewNumber.append(linkTd[3].text)
        loanTime.append(linkTd[5].text)
        returnTime.append(linkTd[6].text)
    response = s.get("http://libopac.ctbu.edu.cn/opac/mylibrary/circulationHistory")
    bs = BeautifulSoup(response.text, 'lxml')
    node = bs.select("#tableHistory")
    link = node[0].find_all("tr")
    for i in range(len(link) - 1):
        tdLink = (link[i + 1].find_all("td"))
        titleHistory.append(tdLink[0].text)
        barCodeHistory.append(tdLink[1].text)
        operation.append(tdLink[2].text)
        timeHistory.append(tdLink[3].text)
        fine.append(tdLink[4].text)
    lenHistory=len(link)
    return jsonify({
        "renewNumber":renewNumber,
        "title":title,
        "barCode" : barCode,
        "loanTime" : loanTime,
        "returnTime":returnTime,
        "textHistory":textHistory,
        "titleHistory":titleHistory,
        "barCodeHistory":barCodeHistory,
        "timeHistory":timeHistory,
        "operation":operation,
        "fine":fine,
        "lenHistory":lenHistory,
    })

@app.route('/title')
def title():
    url = ["http://libopac.ctbu.edu.cn/opac/login", "http://jwsys.ctbu.edu.cn",
           "https://cas.ctbu.edu.cn/lyuapServer/login?service=http%3A%2F%2Fportal.ctbu.edu.cn%2Fc%2Fportal%2Flogin%3Fredirect%3D%252F%26p_l_id%3D70131"]
    title = []
    for i in range(3):
        response = requests.get(url[i])
        bs = BeautifulSoup(response.text, 'lxml')
        node = bs.select("title")
        title.append(node[0].text)
    return jsonify({
        "title":title,
    })


@app.route("/score/<year>/<term>")
def lookScore(year,term):
    global studentNumber
    global studentName
    try:
        if(len(studentNumber)!=0):
            judge1='True'
    except:
        judge1="Null"
    try:
        if(len(studentName)!=0):
            judge2="True"
    except:
        judge2="Null"
    print(judge2)
    print(judge1)
    if(judge2==judge1 and judge1=='True'):
        print('SUCESS')
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

        name = parse.quote(studentName)
        scoreUrl = "http://jwsys.ctbu.edu.cn/xscjcx_dq.aspx?xh=" + studentNumber + "&xm=" + name + "&gnmkdm=N121707"
        referer = "http://jwsys.ctbu.edu.cn/xs_main.aspx?xh=" + studentNumber
        scoreHeaders = {
            "Referer": referer,
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
        judge="True"
    else:
        score = []
        judge="Null"
    return jsonify({'score':score,"judge":judge})

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

    nodeRecord = node1[0].find_all("span")
    record = nodeRecord[0].text
    numberRecord = re.search('\d+', record)
    number = int(numberRecord.group())

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
        print('pages')
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
                # 用于抓取馆藏或可外借或现刊的数据
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
                if (number == "采购中"):
                    print('sucess')
                    part.append('现刊')
                else:
                    ret = re.match('([0-9]*)/([0-9]*)', number)
                    totalNumber = ret.group(1)
                    lent = ret.group(2)
                    collect = '馆藏：' + str(totalNumber)
                    lentOthers = '可外借：' + str(lent)
                    part.append(collect)
                    part.append(lentOthers)
            if (k != len_p):
                # 用于清除多余的符号
                ret1 = re.sub('\n', "", each.text)
                ret2 = re.sub('\t', "", ret1)
                ret3 = re.sub('\r', "", ret2)
                ret = re.sub('\xa0', "", ret3)
                part.append(ret)
        total.append(part)
    global   theSameUrl
    theSameUrl=theSame
    if(len(total)==0):
        judge='Null'
    else:
        judge='True'
    return jsonify({'searchResult': total, 'data1': 1,'judge':judge ,'pages':pages})

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
                # 用于抓取馆藏或可外借或现刊的数据
                link_button = link_p[j].find_all('button')
                bookNumber = link_button[0].get('id')
                bookNumberCode = parse.quote(bookNumber)
                bookNumberUrl = 'http://libopac.ctbu.edu.cn/opac/book/getBookState/' + bookNumber + '/' + bookNumberCode
                responseNumber = requests.get(bookNumberUrl)
                responseNumber.encoding = 'utf-8'
                numberBS = BeautifulSoup(responseNumber.text, 'lxml')
                numberNode = numberBS.select('p')
                number = numberNode[0].text
                if(number=="采购中"):
                    print('sucess')
                    part.append('现刊')
                else:
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
    return jsonify({'storageTitle':storageTitle,'storageDate':storageDate,'judge':'True'})




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


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0')

# # 用于判断是否未定义
# def judgeDefine(var):
#     try:
#         if(len(var)!=0):
#             return "True"
#     except:
#         return 'Null'
