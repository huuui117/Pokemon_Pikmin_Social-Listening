# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 16:55:43 2026

@author: wyz05
"""

# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from urllib.parse import quote

def scrape_ptt_multi_boards_keywords():

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'cookie': 'over18=1'
    }

    # 日期區間
    start_date = datetime(2021, 5, 1)
    end_date = datetime(2026, 5, 31)

    # 五個看板
    boards = [
        'Mobile-game',
        'NSwitch',
        'WomenTalk',
        'Gossiping',
        'C_Chat'
    ]

    # 皮克敏多種講法
    keywords = [
        '皮克敏',
        'Pikmin',
        'pikmin',
        'PIKMIN',
        'Pikmin Bloom',
        '皮克敏Bloom',
        '皮克敏 bloom',
        '皮克敏布魯姆',
        '皮克敏手遊',
        '任天堂皮克敏'
    ]

    all_rows = []

    for board in boards:

        for keyword in keywords:

            current_url = (
                f"https://www.ptt.cc/bbs/{board}/search?q={quote(keyword)}"
            )

            page_count = 1

            print("\n==============================")
            print(f"開始搜尋看板：{board}")
            print(f"關鍵字：{keyword}")
            print("==============================")

            while current_url:

                print(f"正在處理第 {page_count} 頁：{current_url}")

                try:
                    res = requests.get(
                        current_url,
                        headers=headers,
                        timeout=10
                    )

                    if res.status_code != 200:
                        print("無法取得頁面")
                        break

                    soup = BeautifulSoup(res.text, 'html.parser')
                    articles = soup.select('.r-ent')

                    if not articles:
                        print("沒有搜尋結果")
                        break

                    should_stop_early = False

                    for art in articles:

                        title_tag = art.select_one('.title a')

                        if not title_tag:
                            continue

                        title = title_tag.text.strip()
                        author = art.select_one('.author').text.strip()
                        link = "https://www.ptt.cc" + title_tag['href']
                        article_id = (
                            title_tag['href']
                            .split('/')[-1]
                            .replace('.html', '')
                        )

                        try:
                            art_res = requests.get(
                                link,
                                headers=headers,
                                timeout=10
                            )

                            art_soup = BeautifulSoup(
                                art_res.text,
                                'html.parser'
                            )

                            metas = art_soup.select('.article-meta-value')

                            if len(metas) >= 4:
                                board_name = metas[1].text.strip()
                                publish_time_str = metas[3].text.strip()
                            else:
                                board_name = board

                                time_label = art_soup.find(
                                    "span",
                                    class_="article-meta-tag",
                                    string="時間"
                                )

                                if time_label:
                                    publish_time_str = (
                                        time_label
                                        .find_next_sibling("span")
                                        .get_text()
                                        .strip()
                                    )
                                else:
                                    continue

                            try:
                                current_art_date = datetime.strptime(
                                    publish_time_str,
                                    "%a %b %d %H:%M:%S %Y"
                                )
                            except ValueError:
                                continue

                            if current_art_date < start_date:
                                should_stop_early = True
                                continue

                            if current_art_date > end_date:
                                continue

                            category = (
                                title.split(']')[0].replace('[', '')
                                if ']' in title
                                else ''
                            )

                            main_content_tag = art_soup.find(id='main-content')
                            ip = ""

                            if main_content_tag:

                                f2_tags = main_content_tag.select('.f2')

                                for f2 in f2_tags:
                                    if "來自:" in f2.text:
                                        ip = (
                                            f2.text
                                            .split('來自: ')[1]
                                            .split('\n')[0]
                                            .strip()
                                        )

                                temp_soup = BeautifulSoup(
                                    str(main_content_tag),
                                    'html.parser'
                                )

                                for target in temp_soup.select(
                                    '.article-metaline, '
                                    '.article-metaline-right, '
                                    '.push, '
                                    '.push-ad'
                                ):
                                    target.extract()

                                content = temp_soup.get_text().strip()

                            else:
                                content = ""

                            pushes = art_soup.select('.push')
                            comment_list = []
                            push_count = 0
                            boo_count = 0
                            arrow_count = 0

                            for p in pushes:

                                p_tag = (
                                    p.select_one('.push-tag').text.strip() #抓取「推/噓/→」標籤
                                    if p.select_one('.push-tag')
                                    else ""
                                )

                                p_user = (
                                    p.select_one('.push-userid').text.strip() #抓取留言者ID
                                    if p.select_one('.push-userid')
                                    else ""
                                )

                                p_content = (
                                    p.select_one('.push-content') ## 抓取留言內容
                                    .text
                                    .strip(': ')
                                    if p.select_one('.push-content')
                                    else ""
                                )

                                p_time = (
                                    p.select_one('.push-ipdatetime') #抓取留言時間
                                    .text
                                    .strip()
                                    if p.select_one('.push-ipdatetime')
                                    else ""
                                )

                                comment_list.append({ #將留言資料加入列表
                                    'type': p_tag,
                                    'user': p_user,
                                    'content': p_content,
                                    'ipdatetime': p_time
                                })

                                if p_tag == '推': #統計推文數量
                                    push_count += 1 #統計噓文數量
                                elif p_tag == '噓':
                                    boo_count += 1
                                else: #統計箭頭文數量
                                    arrow_count += 1

                            all_rows.append({
                                '搜尋看板': board,
                                '搜尋關鍵字': keyword,
                                '標題': title,
                                '時間': current_art_date.strftime(
                                    '%Y-%m-%d %H:%M:%S'
                                ),
                                '內容': content,
                                '類別': category,
                                '版名': board_name,
                                '文章ID': article_id,
                                '作者': author,
                                'IP': ip,
                                '總留言數': len(comment_list),
                                '留言內容': str(comment_list),
                                '推推總數': push_count,
                                '噓聲總數': boo_count,
                                '中立總數': arrow_count
                            })

                            print("已抓取：", title)

                            time.sleep(1)

                        except Exception as e:
                            print("處理文章錯誤：", e)

                    if should_stop_early:
                        print("已早於起始日期，停止此關鍵字搜尋")
                        break

                    next_btn = soup.find(
                        'a',
                        string=lambda t: t and '上頁' in t
                    )

                    if next_btn and 'href' in next_btn.attrs:
                        current_url = (
                            "https://www.ptt.cc"
                            + next_btn['href']
                        )
                        page_count += 1
                        time.sleep(1)
                    else:
                        current_url = None

                except Exception as e:
                    print("處理搜尋頁錯誤：", e)
                    break

    if all_rows:

        df = pd.DataFrame(all_rows)

        # 去除重複文章
        df = df.drop_duplicates(subset=['文章ID'])

        df.to_csv(
            'ptt_pikmin_multi_boards_keywords.csv',
            encoding='utf-8-sig',
            index=False
        )

        print("\n爬取完成！")
        print("總文章數：", len(df))
        print("檔案名稱：ptt_pikmin_multi_boards_keywords.csv")

    else:
        print("沒有抓到符合條件的資料")


if __name__ == "__main__":
    scrape_ptt_multi_boards_keywords()