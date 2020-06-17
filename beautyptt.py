import sys
import json
import os
from PyPtt import PTT
from Facebooker import facebook
ptt_bot = PTT.API()
fb = facebook.API()
fb.login('fb_account','fb_password')
try:
    ptt_bot.login('ptt_account', 'ptt_password')
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
post_history['latest_post'] = end_index

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
    post = ptt_bot.get_post(
                    Beauty_board,
                    post_aid=post.aid,
                )
    fb_post = '%s\n%s\n%s\n原文連結:%s'%(post.title, post.author, post.content, post.web_url)
    print(post.title)
    post_history[post.aid] = post.content
    fb.fanpage_post(fb_post,'fanpage_id')
    with open('posts.json', 'w') as f:
        json.dump(post_history, f, ensure_ascii=False)

