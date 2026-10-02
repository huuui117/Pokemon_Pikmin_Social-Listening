# -*- coding: utf-8 -*-
"""
PTT PokemonGO 資料清理
產出三個檔案：
1. ptt_pokemon_go_combined_clear.csv
2. ptt_pokemon_go_combined_comments.csv
3. ptt_pokemon_go_comments_merged.csv
"""

import pandas as pd
import ast
import re

# ==========================
# 讀取寶可夢原始資料
# ==========================

ptt_data = pd.read_csv('ptt_pokemon_go_202105_202605.csv')

# 去除重複與空白
ptt_data = ptt_data.drop_duplicates()
ptt_data = ptt_data.dropna()

# 修改時間格式
ptt_data['時間'] = pd.to_datetime(ptt_data['時間'])

# 計算留言總數
ptt_data['留言總數'] = (
    ptt_data['推推總數']
    + ptt_data['噓聲總數']
    + ptt_data['中立總數']
)

# 去除公告
ptt_data = ptt_data[ptt_data['類別'] != '公告']

# ==========================
# 建立「所有文」
# ==========================

ptt_data['所有文'] = (
    ptt_data['標題'].astype(str)
    + ptt_data['內容'].astype(str)
)

# ==========================
# 移除無意義字元
# ==========================

removeword = [
    'span','class','f3','https','http','www','imgur',
    'jpg','jpeg','png','gif','webp',
    'href','rel','nofollow','target',
    'cdn','cgi','html','email','data',
    'bbs','ptt','cc',
    '原文內容','原文連結',
    '作者','標題','時間','看板',
    '<','>','，','。','？','！','：','；',
    '、','「','」','『','』','【','】',
    '（','）','(',')','[',']',
    '《','》','/','\\','|',
    '\n','\r','\t',' ',
    '=','"',"'",'~','～','@','#',
    '$','%','^','&','*','+',
    '※','--','…','・','‧',
    'XD','XDD','QQ'
]

for word in removeword:
    ptt_data['所有文'] = ptt_data['所有文'].str.replace(
        word,
        '',
        regex=False
    )

# 移除網址
ptt_data['所有文'] = ptt_data['所有文'].str.replace(
    r'https?://\S+|www\.\S+',
    '',
    regex=True
)

# ==========================
# 儲存第一個檔案
# ==========================

ptt_data.to_csv(
    'ptt_pokemon_go_combined_clear.csv',
    encoding='utf-8-sig',
    index=False
)

print('第一個檔案完成：ptt_pokemon_go_combined_clear.csv')

# ==========================
# 展開留言內容
# ==========================

newlist = []

for i in range(len(ptt_data)):

    try:
        comments = ast.literal_eval(ptt_data['留言內容'].iloc[i])

        if len(comments) > 0:
            temp = pd.DataFrame(comments)
            newlist.append(temp)

    except:
        continue

ptt_comment = pd.concat(
    newlist,
    ignore_index=True
)

# 確保欄位順序跟範例一樣
ptt_comment = ptt_comment[
    ['type', 'user', 'content', 'ipdatetime']
]

# ==========================
# 清理留言內容
# ==========================

ptt_comment['content'] = ptt_comment['content'].astype(str)

# 移除圖片與網址
ptt_comment['content'] = ptt_comment['content'].str.replace(
    r'https?://\S+|www\.\S+|imgur\.com/\S+|i\.imgur\.com/\S+',
    '',
    regex=True
)

# 移除圖片副檔名
ptt_comment['content'] = ptt_comment['content'].str.replace(
    r'\S+\.(jpg|jpeg|png|gif|webp)',
    '',
    regex=True
)

# 移除前後空白
ptt_comment['content'] = ptt_comment['content'].str.strip()

# 移除無意義留言
bad_comments = [
    '',
    'done',
    'Done',
    'DONE',
    'ok',
    'OK',
    'thanks',
    'thank',
    '謝謝',
    '感謝',
    '+1',
    '+',
    '已加',
    '已寄',
    '收信',
    '站內',
    '站內信'
]

ptt_comment = ptt_comment[
    ~ptt_comment['content'].isin(bad_comments)
]

# ==========================
# 儲存第二個檔案
# ==========================

ptt_comment.to_csv(
    'ptt_pokemon_go_combined_comments.csv',
    encoding='utf-8-sig',
    index=False
)

print('第二個檔案完成：ptt_pokemon_go_combined_comments.csv')

# ==========================
# 製作第三個 merged 檔案
# 欄位順序改成 user, type, content, ipdatetime
# ==========================

ptt_comment_merged = ptt_comment[
    ['user', 'type', 'content', 'ipdatetime']
]

ptt_comment_merged.to_csv(
    'ptt_pokemon_go_comments_merged.csv',
    encoding='utf-8-sig',
    index=False
)

print('第三個檔案完成：ptt_pokemon_go_comments_merged.csv')

print('全部完成！')
print('文章資料筆數：', len(ptt_data))
print('留言資料筆數：', len(ptt_comment))