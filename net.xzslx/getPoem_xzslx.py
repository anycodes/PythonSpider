import urllib.request
from lxml import etree
import re
import pymongo
import json
import socket
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def get_ip():
    # pass
    for i in range(1, 100):
        try:

            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

            url_attr = urllib.request.Request("http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp")
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


MONGODB_DBNAME = 'ChinesePoem'
tdb = linkDatabase(MONGODB_DBNAME)
for page in range(1,5669):
    try:
        url = "https://www.xzslx.net/gushi/0/0/0/0/0/%d/"%(page)
        pageSource = urllib.request.urlopen(url).read().decode("utf-8")
        xpathAttr = etree.HTML(pageSource)
        for eveContent in xpathAttr.xpath("//div[@class='leftcon']"):
            poem = {}
            poem['title'] = "".join(eveContent.xpath("strong//text()")).strip()
            poem['author'] = "".join(eveContent.xpath("span[1]//text()")).replace("作者：","").strip()
            content = "".join(eveContent.xpath("p/text()")).replace("\n","").strip()
            poem['tempContent'] = "".join(re.findall(r'[\u4e00-\u9fa5]|，|。|\?|!',content))
            print(poem['title'])
            if len(poem['title'])>0:
                post = tdb["poem"]
                post.insert(poem)
    except Exception as e:
        print(url)
        get_ip()

