import pymongo
import socket


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


MONGODB_DBNAME = 'dbmovie'
tdb = linkDatabase(MONGODB_DBNAME)


import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.request
import json


# -----------获得电影

# urlList = [
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=time&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%96%87%E8%89%BA&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%81%90%E6%80%96&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%82%AC%E7%96%91&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%A7%91%E5%B9%BB&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%88%B1%E6%83%85&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%96%9C%E5%89%A7&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%8A%A8%E4%BD%9C&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%97%A5%E6%9C%AC&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E9%9F%A9%E5%9B%BD&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%AC%A7%E7%BE%8E&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%8D%8E%E8%AF%AD&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%86%B7%E9%97%A8%E4%BD%B3%E7%89%87&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E8%B1%86%E7%93%A3%E9%AB%98%E5%88%86&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%8F%AF%E6%92%AD%E6%94%BE&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%BB%8F%E5%85%B8&sort=recommend&page_limit=20&page_start=",
#     "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%9C%80%E6%96%B0&page_limit=20&page_start=",
# ]
#
#
# for url in urlList:
#     countData = 20
#     startNum = 0
#     idList = []
#
#     while countData == 20:
#         movieData = url + str(startNum)
#         print(movieData)
#         jsonData = json.loads(urllib.request.urlopen(movieData).read().decode("utf-8"))
#         countData = len(jsonData["subjects"])
#         for eve in jsonData["subjects"]:
#             print(eve)
#             if eve["id"] not in idList:
#                 idList.append(eve["id"])
#                 with open("idList.txt", "a") as f:
#                     f.write(eve["id"] + "\t")
#                 post = tdb["movieData"]
#                 post.insert(eve)
#
#         startNum = startNum + 20


# ------------获得评论
import re
from lxml import etree
from pymongo import MongoClient
conn = MongoClient('127.0.0.1', 27017)
db = conn.dbmovie
movideData = db.movieData.find()

for eveMovie in movideData:
    mID = eveMovie["id"]
    reviewListUrl = "https://movie.douban.com/subject/%s/reviews?start="%(mID)
    totalCount = 20
    thisCount = 0
    while totalCount >= thisCount:
        reviewListUrlData = reviewListUrl + str(thisCount)
        sourceData = urllib.request.urlopen(reviewListUrlData).read().decode("utf-8")
        totalCount = int(re.findall('\((.*?)\)',sourceData)[0])
        thisCount = thisCount + 20

        centerData = sourceData.split('<script type="text/javascript" src="https://img3.doubanio.com/misc/mixed_static/2163464e211f6769.js"></script>')[0].split('<div class="review-list  ">')[1]
        tenpList = centerData.split('<div xmlns:v="http://rdf.data-vocabulary.org/#"')
        tempListData = []
        print(reviewListUrlData)
        for eveTemp in tenpList:

            if eveTemp.replace("\n","").strip():
                try:
                    rID = re.findall('data-cid="(.*?)"', eveTemp)[0]
                    try:
                        fenshu = re.findall('main-title-rating" title="(.*?)"></span>', eveTemp)[0]
                    except:
                        fenshu = "none"
                    try:
                        user = re.findall('class="name">(.*?)</a>', eveTemp)[0]
                    except:
                        user = "none"
                    try:
                        timdata = re.findall('class="main-meta">(.*?)</span>', eveTemp)[0]
                    except:
                        timdata = "none"

                    print(rID,fenshu,user,timdata)


                    eveId = rID
                    username = user
                    timeD = timdata
                    score = fenshu
                    print(eveId,score)
                    reviewContentUrl = "https://movie.douban.com/j/review/%s/full"%(eveId)
                    jsonData = json.loads(urllib.request.urlopen(reviewContentUrl).read().decode("utf-8"))
                    jsonData["movieId"] = mID
                    jsonData["score"] = score
                    jsonData["user"] = username
                    jsonData["date"] = timeD
                    post = tdb["commentData"]
                    post.insert(jsonData)
                except:
                    pass

