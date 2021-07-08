from encrypt import encrypt
import json
import requests
import hashlib
import random
import datetime


# Calculate the MD5 value of text
def calc_md5(text):
    md5_text = hashlib.md5(text.encode(encoding="utf-8")).hexdigest()
    return md5_text


def login(phone, country_code, password):
    session = requests.Session()
    login_url = "https://music.163.com/weapi/login/cellphone"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/84.0.4147.89 Safari/537.36",
        "Referer":
        "http://music.163.com/",
        "Accept-Encoding":
        "gzip, deflate",
        "Cookie":
        "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; "
        "channel=netease; __remember_me=true;",
    }
    login_data = encrypt(
        json.dumps({
            "phone": phone,
            "countrycode": country_code,
            "password": calc_md5(password),
            "rememberLogin": "true"
        }))
    res = session.post(url=login_url, data=login_data, headers=headers)
    ret = json.loads(res.text)
    print(ret)
    if ret["code"] == 200:
        return res.cookies
    return None


def sign(csrf, cookie):
    session = requests.Session()
    sign_url = "https://music.163.com/weapi/point/dailyTask?{csrf}".format(
        csrf=csrf)
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/84.0.4147.89 Safari/537.36",
        "Referer":
        "http://music.163.com/",
        "Accept-Encoding":
        "gzip, deflate",
        "Cookie":
        cookie,
    }
    res_m = session.post(url=sign_url,
                         data=encrypt('{{"type":{0}}}'.format(0)),
                         headers=headers)
    res_pc = session.post(url=sign_url,
                          data=encrypt('{{"type":{0}}}'.format(1)),
                          headers=headers)
    ret_m = json.loads(res_m.text)
    ret_pc = json.loads(res_pc.text)

    res = {"mobile": 0, "pc": 0}

    if ret_m["code"] == 200:
        res["mobile"] = ret_m["point"]
    if ret_pc["code"] == 200:
        res["pc"] = ret_pc["point"]
    return res


def task(csrf, cookie):
    session = requests.Session()
    feedback_url = "http://music.163.com/weapi/feedback/weblog"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/84.0.4147.89 Safari/537.36",
        "Referer":
        "http://music.163.com/",
        "Accept-Encoding":
        "gzip, deflate",
        "Cookie":
        cookie,
    }
    post_data = json.dumps({
        "logs":
        json.dumps(
            list(
                map(
                    lambda x: {
                        "action": "play",
                        "json": {
                            "download": 0,
                            "end": "playend",
                            "id": x,
                            "sourceId": "",
                            "time": 240,
                            "type": "song",
                            "wifi": 0,
                        },
                    },
                    get_musics(csrf=csrf, headers=headers),
                )))
    })
    res = session.post(url=feedback_url, data=encrypt(post_data))
    ret = json.loads(res.text)
    if ret["code"] == 200:
        text = "刷听歌量成功"
    else:
        text = "刷听歌量失败 " + str(ret["code"]) + "：" + ret["message"]
    return text


def get_musics(csrf, headers):
    detail_url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + csrf
    musics = []
    for m in get_recommend_playlists(csrf, headers):
        res = requests.post(
            url=detail_url,
            data=encrypt(json.dumps({
                "id": m,
                "n": 1000,
                "csrf_token": csrf
            })),
            headers=headers,
        )
        ret = json.loads(res.text)
        musics.extend([i["id"] for i in ret["playlist"]["trackIds"]])
    return musics


def get_recommend_playlists(csrf, headers):
    recommend_url = "https://music.163.com/weapi/v1/discovery/recommend/resource"
    res = requests.post(url=recommend_url,
                        data=encrypt('{"csrf_token":"' + csrf + '"}'),
                        headers=headers)
    ret = json.loads(res.text)
    playlists = []
    if ret["code"] == 200:
        playlists.extend([(d["id"]) for d in ret["recommend"]])
    return playlists
