from fastapi import Header, FastAPI, Cookie
from fastapi.responses import JSONResponse
from task import login, sign, task
import requests

app = FastAPI()


@app.get("/login/cellphone")
async def login_cellphone(phone: str = "",
                          country_code: int = "",
                          password: str = ""):
    res = login(phone, country_code, password)
    content = {"code": 0, "message": "登录成功"}
    cookies = requests.utils.dict_from_cookiejar(res)
    response = JSONResponse(content=content)
    response.set_cookie(key="MUSIC_U", value=cookies["MUSIC_U"])
    response.set_cookie(key="NMTID", value=cookies["NMTID"])
    response.set_cookie(key="__csrf", value=cookies["__csrf"])
    response.set_cookie(key="__remember_me", value=cookies["__remember_me"])
    return response


@app.get("/task/sign")
async def task_sign(__csrf: str = Cookie(None), cookie: str = Header(None)):
    res = sign(__csrf, cookie)
    return {
        "code":
        0,
        "message":
        "安卓端签到成功，经验加{0}; PC/Web端签到成功，经验加{1}".format(res["mobile"], res["pc"]),
    }


@app.get("/task/music")
async def task_music(__csrf: str = Cookie(None), cookie: str = Header(None)):
    res = task(__csrf, cookie)
    return {"code": 0, "message": res}
