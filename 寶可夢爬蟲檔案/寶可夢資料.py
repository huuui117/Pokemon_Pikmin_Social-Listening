# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 16:04:17 2026

@author: wyz05
"""

# -*- coding: utf-8 -*-

import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.ptt.cc"
START_URL = "https://www.ptt.cc/bbs/PokemonGO/index961.html"
OUTPUT_CSV = "ptt_pokemon_go_202105_202605.csv"

# 資料區間：2021 年 5 月到 2026 年 5 月
START_DATE = datetime(2021, 5, 1, 0, 0, 0)
END_DATE = datetime(2026, 5, 31, 23, 59, 59)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "cookie": "over18=1",
}


session = requests.Session()
session.headers.update(HEADERS)


def get_soup(url):
    """取得網頁 BeautifulSoup 物件。"""
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except requests.RequestException as e:
        print(f"讀取失敗：{url}，原因：{e}")
        return None


def parse_ptt_time(time_text):
    """將 PTT 文章頁面的時間字串轉成 datetime。"""
    try:
        return datetime.strptime(time_text, "%a %b %d %H:%M:%S %Y")
    except Exception:
        return None


def extract_article(link, list_author="", list_date=""):
    """爬取單篇文章內容與留言。"""
    soup = get_soup(link)
    if soup is None:
        return None

    metas = soup.select(".article-meta-value")
    if len(metas) < 4:
        return None

    author = metas[0].get_text(strip=True) if len(metas) >= 1 else list_author
    board_name = metas[1].get_text(strip=True) if len(metas) >= 2 else "PokemonGO"
    title = metas[2].get_text(strip=True) if len(metas) >= 3 else ""
    publish_time_str = metas[3].get_text(strip=True) if len(metas) >= 4 else ""
    publish_dt = parse_ptt_time(publish_time_str)

    if publish_dt is None:
        return None

    # 日期篩選
    if publish_dt < START_DATE:
        return {"too_old": True, "publish_dt": publish_dt}
    if publish_dt > END_DATE:
        return {"skip": True, "publish_dt": publish_dt}

    article_id = link.split("/")[-1].replace(".html", "")
    category = title.split("]")[0].replace("[", "") if "]" in title else ""

    main_content_tag = soup.find(id="main-content")
    ip = ""
    content = ""

    if main_content_tag:
        # 取得發文 IP
        for f2 in main_content_tag.select(".f2"):
            f2_text = f2.get_text(strip=True)
            if "來自:" in f2_text:
                ip = f2_text.split("來自:")[-1].strip()

        # 移除標頭、留言、系統資訊，只留下文章內文
        temp_soup = BeautifulSoup(str(main_content_tag), "html.parser")
        for target in temp_soup.select(
            ".article-metaline, .article-metaline-right, .push, .push-ad, .f2"
        ):
            target.extract()
        content = temp_soup.get_text("\n", strip=True)

    # 留言處理
    pushes = soup.select(".push")
    comment_list = []
    push_count = 0
    boo_count = 0
    arrow_count = 0

    for p in pushes:
        p_tag = p.select_one(".push-tag").get_text(strip=True) if p.select_one(".push-tag") else ""
        p_user = p.select_one(".push-userid").get_text(strip=True) if p.select_one(".push-userid") else ""
        p_content = p.select_one(".push-content").get_text(strip=True).lstrip(": ") if p.select_one(".push-content") else ""
        p_time = p.select_one(".push-ipdatetime").get_text(strip=True) if p.select_one(".push-ipdatetime") else ""

        comment_list.append({
            "type": p_tag,
            "user": p_user,
            "content": p_content,
            "ipdatetime": p_time,
        })

        if p_tag == "推":
            push_count += 1
        elif p_tag == "噓":
            boo_count += 1
        else:
            arrow_count += 1

    return {
        "too_old": False,
        "skip": False,
        "標題": title,
        "時間": publish_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "列表日期": list_date,
        "內容": content,
        "類別": category,
        "版名": board_name,
        "文章ID": article_id,
        "作者": author or list_author,
        "IP": ip,
        "文章連結": link,
        "總留言數": len(comment_list),
        "留言內容": str(comment_list),
        "推推總數": push_count,
        "噓聲總數": boo_count,
        "中立總數": arrow_count,
    }


def get_previous_page_url(soup):
    """取得 PTT 列表頁的「上頁」連結。"""
    btn = soup.find("a", string=lambda t: t and "上頁" in t)
    if btn and btn.get("href"):
        return BASE_URL + btn["href"]
    return None


def scrape_ptt_pokemongo():
    current_url = START_URL
    all_rows = []
    page_count = 1

    print(f"開始爬取 PokemonGO 版")
    print(f"資料區間：{START_DATE.date()} ~ {END_DATE.date()}")
    print(f"起始頁面：{START_URL}")

    while current_url:
        print(f"\n正在處理第 {page_count} 個列表頁：{current_url}")
        soup = get_soup(current_url)
        if soup is None:
            break

        articles = soup.select(".r-ent")
        if not articles:
            print("此頁沒有文章，停止。")
            break

        should_stop = False

        # PTT 列表通常由舊到新排列；整頁處理完再往上頁，也就是更舊頁面
        for art in articles:
            title_tag = art.select_one(".title a")
            if not title_tag:
                continue

            title_in_list = title_tag.get_text(strip=True)
            author_in_list = art.select_one(".author").get_text(strip=True) if art.select_one(".author") else ""
            date_in_list = art.select_one(".date").get_text(strip=True) if art.select_one(".date") else ""
            link = BASE_URL + title_tag["href"]

            print(f"正在檢查文章：{title_in_list}")
            data = extract_article(link, author_in_list, date_in_list)

            if data is None:
                time.sleep(0.5)
                continue

            if data.get("too_old"):
                should_stop = True
                continue

            if data.get("skip"):
                time.sleep(0.5)
                continue

            all_rows.append(data)
            print(f"已加入：{data['時間']}｜{data['標題']}")
            time.sleep(0.8)  # 避免請求過快

        if should_stop:
            print("已遇到早於 2021-05-01 的文章，停止往更舊頁面爬取。")
            break

        current_url = get_previous_page_url(soup)
        page_count += 1
        time.sleep(1)

    if all_rows:
        df = pd.DataFrame(all_rows)
        df = df.sort_values("時間", ascending=True).reset_index(drop=True)
        df.to_csv(OUTPUT_CSV, index_label="Unnamed: 0", encoding="utf-8-sig")
        print(f"\n爬取完成！共抓取 {len(df)} 篇文章")
        print(f"檔案已輸出：{OUTPUT_CSV}")
    else:
        print("\n沒有抓到符合日期區間的文章。")


if __name__ == "__main__":
    scrape_ptt_pokemongo()
