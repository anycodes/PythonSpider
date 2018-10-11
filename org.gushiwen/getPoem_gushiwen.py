import urllib.request
import re
from lxml import etree
import json
import socket
import time
import pymongo
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# totalAuthor = []
# for page in range(1,623):
#     authorList = "https://so.gushiwen.org/authors/default.aspx?p=%d&c="%(page)
#     pageSource = urllib.request.urlopen(authorList).read().decode("utf-8")
#     listData = re.findall("/authorv_(.*?).aspx", pageSource)
#     totalAuthor = totalAuthor + listData
#
# totalAuthor = list(set(totalAuthor))
#
# with open("author.txt", "w") as f:
#     f.write("\n".join(totalAuthor))


def get_ip():
    # pass
    for i in range(1, 100):
        try:

            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

            url_attr = urllib.request.Request("http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?")
            ip_temp = urllib.request.urlopen(url_attr)
            ip = ip_temp.read().decode("utf-8")
            ip_acount = json.loads(ip)["RESULT"][0]
            port = str(ip_acount["port"])
            ip_add = str(ip_acount["ip"])
            main_ip = ip_add + ":" + port
            temp_url = "http://ip.chinaz.com/getip.aspx"
            proxy_support = urllib.request.ProxyHandler({'http': main_ip})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
            socket.setdefaulttimeout(3)
            res = urllib.request.urlopen(temp_url).read().decode('utf-8')
            print('This ip is ok : ', res)
            break
        except Exception as e:
            print(e)
            time.sleep(5)
            continue

def linkDatabase(MONGODB_DBNAME,MONGODB_HOST='127.0.0.1',MONGODB_PORT=27017):
    '''
    链接MongoDB数据库
    :param MONGODB_HOST: 数据库HOST，默认本地IP，127.0.0.1
    :param MONGODB_PORT: 数据库PORT，默认端口，27017
    :param MONGODB_DBNAME: 数据库名字
    :return: 对象
    '''
    host = MONGODB_HOST
    port = MONGODB_PORT
    dbName = MONGODB_DBNAME
    client = pymongo.MongoClient(host=host, port=port)
    tdb = client[dbName]
    return tdb

with open("author.txt") as f:
    authorData = [eveData.strip() for eveData in f.readlines()]


MONGODB_DBNAME = 'ChinesePoem'
tdb = linkDatabase(MONGODB_DBNAME)

for eveAuthor in authorData:
    pageCount = 1

    for page in range(1,int(pageCount) + 1):
        try:
            urlData = "https://so.gushiwen.org/authors/authorvsw_%sA%d.aspx" % (eveAuthor, page)

            if page == 1:
                pageSource = urllib.request.urlopen(urlData).read().decode("utf-8")
                pageCount = re.findall('<span style=" background-color:#E1E0C7; border:0px; margin-top:22px; width:auto;">/ (.*?)页</span>',pageSource)[0]

            pageSource = urllib.request.urlopen(urlData).read().decode("utf-8")
            xpathData = etree.HTML(pageSource)
            for eveContent in xpathData.xpath("//div[@class='sons']"):
                title = "".join(eveContent.xpath('div[1]/p[1]//text()'))
                dan,_,author = eveContent.xpath('div[1]/p[2]//text()')
                temp = eveContent.xpath('div[1]/div[2]//text()')
                content = "".join([eveData.strip() for eveData in temp])
                tempList = {
                    "title":title,
                    "dan":dan,
                    "author":author,
                    "content":content
                }
                post = tdb["poem11"]
                post.insert(tempList)
                print(tempList["title"])
        except Exception as e:
            with open("errorList.txt", "a") as f:
                f.write(urlData + "\n")
            print(urlData)
            get_ip()
