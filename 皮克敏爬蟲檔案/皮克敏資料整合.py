# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 17:09:40 2026

@author: wyz05
"""

import pandas as pd
import ast

# ==========================
# 讀取五個皮克敏原始資料
# ==========================

file_names = [
    'ptt_pikmin_multi_boards_keywords.csv'
]

df_list = []

for file in file_names:
    try:
        temp = pd.read_csv(file)
        df_list.append(temp)
        print("成功讀取：", file)
    except FileNotFoundError:
        print("找不到檔案：", file)

ptt_data = pd.concat(df_list, ignore_index=True)

# ==========================
# 基本清理
# ==========================

ptt_data = ptt_data.drop_duplicates()
ptt_data = ptt_data.dropna(subset=['標題', '內容', '留言內容'])

ptt_data['時間'] = pd.to_datetime(ptt_data['時間'], errors='coerce')
ptt_data = ptt_data.dropna(subset=['時間'])

ptt_data['留言總數'] = (
    ptt_data['推推總數']
    + ptt_data['噓聲總數']
    + ptt_data['中立總數']
)

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

ptt_data['所有文'] = ptt_data['所有文'].str.replace(
    r'https?://\S+|www\.\S+',
    '',
    regex=True
)

ptt_data = ptt_data[ptt_data['所有文'].str.strip() != '']

# ==========================
# 儲存第一個檔案
# ==========================

ptt_data.to_csv(
    'ptt_pikmin_combined_clear.csv',
    encoding='utf-8-sig',
    index=False
)

print('第一個檔案完成：ptt_pikmin_combined_clear.csv')

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

ptt_comment = ptt_comment[
    ['type', 'user', 'content', 'ipdatetime']
]

# ==========================
# 清理留言內容
# ==========================

ptt_comment['content'] = ptt_comment['content'].astype(str)

ptt_comment['content'] = ptt_comment['content'].str.replace(
    r'https?://\S+|www\.\S+|imgur\.com/\S+|i\.imgur\.com/\S+',
    '',
    regex=True
)

ptt_comment['content'] = ptt_comment['content'].str.replace(
    r'\S+\.(jpg|jpeg|png|gif|webp)',
    '',
    regex=True
)

ptt_comment['content'] = ptt_comment['content'].str.strip()

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
    'ptt_pikmin_combined_comments.csv',
    encoding='utf-8-sig',
    index=False
)

print('第二個檔案完成：ptt_pikmin_combined_comments.csv')

# ==========================
# 製作第三個 merged 檔案
# 依照 user 合併留言
# ==========================

ptt_comment_merged = ptt_comment.groupby('user').agg({
    'type': 'first',
    'content': ' '.join,
    'ipdatetime': 'first'
}).reset_index()

ptt_comment_merged = ptt_comment_merged[
    ['user', 'type', 'content', 'ipdatetime']
]

ptt_comment_merged.to_csv(
    'ptt_pikmin_comments_merged.csv',
    encoding='utf-8-sig',
    index=False
)

print('第三個檔案完成：ptt_pikmin_comments_merged.csv')

print('全部完成！')
print('文章資料筆數：', len(ptt_data))
print('留言資料筆數：', len(ptt_comment))
print('合併後使用者數：', len(ptt_comment_merged))