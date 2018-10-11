import re
import urllib.request
import urllib.parse
import json
import pymongo
import socket
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


headers = {
    "Referer": "http://music.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
}


def get_ip():
    # pass
    for i in range(1, 100):
        try:

            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

            url_attr = urllib.request.Request("http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?",headers=headers)
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

def getId(idData):
    url = "https://music.163.com/artist?id=%s"%(idData)
    pageSource = urllib.request.urlopen(urllib.request.Request(url=url,headers=headers)).read().decode("utf-8")
    # songsId = re.findall('song\?id=(.*?)"',pageSource)
    commentId = re.findall('"commentThreadId":"(.*?)"',pageSource)
    return commentId


def getComments(commentId,offset):
    url = "http://music.163.com/weapi/v1/resource/comments/%s?csrf_token="%(commentId)
    rid = re.findall('comments/(.*?)\?', url)[0]
    params_first = '{"rid":"%s","offset":"%d","total":"false","limit":"100","csrf_token":""}' % (rid, offset)
    params_second = "010001"
    params_third = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    params_forth = "0CoJUm6Qyw8W8jud"

    with open("yunJS.js") as f:
        data = f.read()

    import execjs

    getParams = execjs.compile(data).call("d", params_first, params_second, params_third, params_forth)

    formData = {
        "params": getParams["encText"],
        "encSecKey": getParams["encSecKey"]
    }

    jsonData = json.loads(urllib.request.urlopen(urllib.request.Request(url=url, data=urllib.parse.urlencode(formData).encode("utf-8"),headers=headers)).read().decode("utf-8"))
    return (jsonData["comments"],jsonData["total"])


def getPlayerId(id,initial):
    url = "https://music.163.com/discover/artist/cat?id=%d&initial=%d"%(id,initial)
    pageSource = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers)).read().decode("utf-8")
    players = re.findall('href="/artist\?id=(.*?)"', pageSource)
    return players



idList = [1001,1002,1003,2001,2002,2003,6001,6002,6003,7001,7002,7003,4001,4002,4003]
initial = [65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90]
MONGODB_DBNAME = 'wyspider'
tdb = linkDatabase(MONGODB_DBNAME)


for eveId in idList:
    for eveInit in initial:
        playerIds = getPlayerId(eveId, eveInit)
        for evePlyer in playerIds:
            commentsData = getId(evePlyer)
            for eveComments in commentsData:

                offsetData = 100
                stopData = 0
                totalData = []
                TOTALCOUNT = 100
                while TOTALCOUNT >= offsetData:
                    try:
                        print("---------%s---------%s---------"%(eveComments,offsetData))
                        commentTemp = getComments(eveComments,offsetData)
                        comments = commentTemp[0]
                        TOTALCOUNT = int(commentTemp[1])
                        offsetData = offsetData + 100
                        for eve in comments:
                            if eve["content"] in totalData:
                                stopData = stopData + 1
                                if stopData > 3:
                                    break
                            else:
                                totalData.append(eve)
                                eve["musicinfor"] = eveComments
                                post = tdb["comments"]
                                post.insert(eve)

                        print("---------获得了%d条数据,一共%d条数据---------" % (len(comments), TOTALCOUNT))

                        if len(comments) < 100:
                            break

                    except Exception as e:
                        get_ip()
                        print(e)




