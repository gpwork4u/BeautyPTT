import sys
import json
import os
import time
import re
import requests
from io import BytesIO
from configparser import ConfigParser
from PyPtt import PTT
from Facebooker import facebook
ptt_bot = PTT.API()
fb = facebook.API()
config = ConfigParser()
config.read('config.ini')
fb_account = config.get('facebook','account')
fb_password = config.get('facebook','password')
fanpage_id = config.get('facebook','fanpage_id')
ptt_account = config.get('PTT','account')
ptt_password = config.get('PTT','password')

fb.login(fb_account, fb_password)
try:
    ptt_bot.login(ptt_account, ptt_password)
except PTT.exceptions.LoginError:
    ptt_bot.log('登入失敗')
    sys.exit()
except PTT.exceptions.WrongIDorPassword:
    ptt_bot.log('帳號密碼錯誤')
    sys.exit()
except PTT.exceptions.LoginTooOften:
    ptt_bot.log('請稍等一下再登入')
    sys.exit()
ptt_bot.log('登入成功')

Beauty_board = 'Beauty'

posts = []
post_history = {}
newest_index = ptt_bot.get_newest_index(
                    PTT.data_type.index_type.BBS,
                    board=Beauty_board
               )

start_index = newest_index / 2

if os.path.isfile('posts.json'):
    with open('posts.json', 'r') as f:
        post_history = json.load(f)
    start_index = int(post_history['latest_post'])



end_index = start_index + 1000

for i in range(start_index,end_index):
    print('%d/%d'%(i+1-start_index, end_index-start_index))
    try:
        post_info = ptt_bot.get_post(
                        Beauty_board,
                        post_index=i,
                        query=True
                    )
    except Exception:
        continue
    
    try:
        if post_info.title.find('[投稿]') >= 0 or post_info.title.find('[公告]') >= 0 :
            continue
        if post_info.push_number == '爆':
            posts.append(post_info)
        elif int(post_info.push_number) >= 30:
            posts.append(post_info)
    except:
        pass

for post in posts:
    if post.aid in post_history:
        continue
    try:
        post = ptt_bot.get_post(
                        Beauty_board,
                        post_aid=post.aid,
                    )
    except Exception:
        ptt_bot.login(ptt_account, ptt_password)
        post = ptt_bot.get_post(
                        Beauty_board,
                        post_aid=post.aid,
                    )
    fb_post = '原文連結:%s\n%s\n%s\n%s'%(post.web_url, post.title, post.author, post.content)
    match = re.search('http(s|)://i.imgur.com/(.+/|)[a-zA-Z0-9]+(\.jpg|)', post.content)
    print(post.title)
    if match:
        img_url = match.group(0)
        if img_url.find('.jpg') < 0:
            img_url += '.jpg'
        print('match image:%s'%img_url)

        response = requests.get(img_url)
        if response.status_code == 200:
            image = BytesIO(response.content)
            fb.fanpage_post_photo(fb_post, image, fanpage_id)
    else:
        post_history[post.aid] = post.content
        post_history['latest_post'] = post.index
        fb.fanpage_post(fb_post, fanpage_id)
    with open('posts.json', 'w') as f:
        json.dump(post_history, f, ensure_ascii=False)
    time.sleep(600)


