# -*- coding: utf-8 -*-
from ast import pattern
import feedparser
import requests
import json
import urllib
import math
import re
from bs4 import BeautifulSoup

session = requests.session()


def search_anime_bangumi(keywords, type=2, start=1, max_results=10):
    """Get anime id which you want to watch from bangumi.

    Args:
        keywords: Name of anime.
        type: Subject Type.
        start: Query page
        max_results: Each page of max number of results.


    Returns:
        Anime ID: A integer.
    """
    search_api_url = "https://api.bgm.tv/search/subject/"
    search_value = {}
    search_value['type'] = type  # 2 = Anime
    search_value['start'] = start  # 开始条数
    search_value['max_results'] = max_results  # 每页条数 maximum: 25
    max_page = start + 1
    dict_result = {}
    anime_list = []
    chosen_index = -1

    while (0 > chosen_index or max_results <= chosen_index) and search_value["start"] <= max_page:
        try:
            url = search_api_url + keywords + "?" + \
                urllib.parse.urlencode(search_value)
            r = requests.get(url=url)
            dict_result = json.loads(r.content.decode("utf-8"))
            max_page = math.ceil(dict_result['results'] / max_results)
            anime_list = dict_result['list']
            print(f"\n第{search_value['start']}页\n")
            for index, anime_item in enumerate(anime_list):
                print("########################")
                print(
                    f"索引: {index}\n标题 {anime_item['name']}\n中文标题 {anime_item['name_cn']}")
            chosen_index = int(input("输入选择动漫的索引,如无匹配结果直接回车进入下一页"))
            search_value["start"] += 1
        except BaseException as e:
            print(e)
            return -1
    print(
        f"当前选择为: \n索引: {int(chosen_index)}\n标题 {anime_list[int(chosen_index)]['name']}\n中文标题 {anime_list[int(chosen_index)]['name_cn']}")
    return anime_list[int(chosen_index)]['id']


def search_bangumi_mikan(bangumi_keywords: str) -> tuple[int, str]:
    """Get anime id which you want to watch from bangumi.

    Args:
        keywords: Name of anime.
        type: Subject Type.
        start: Query page
        max_results: Each page of max number of results.


    Returns:
        Anime ID: str.
    """
    search_value = {}
    search_value['searchstr'] = bangumi_keywords
    mikan_base_url = "https://mikanani.me/Home/Search?"

    url = mikan_base_url + urllib.parse.urlencode(search_value)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}
    r = requests.get(url=url, headers=headers).text

    soup = BeautifulSoup(r, "html.parser")
    bangumi_list = soup.select("ul.an-ul>li")

    for index, item in enumerate(bangumi_list):
        title = item.find("div", class_="an-text")['title']
        print("########################")
        print(f"索引: {index}\n标题:  {title}")
    chosen_index = input("输入选择动漫的索引,如无匹配结果直接回车退出")
    if chosen_index == "":
        return (-1,"")
    bangumi_id = int(bangumi_list[int(chosen_index)].a['href'].split("/")[-1])
    return (bangumi_id, bangumi_list[int(chosen_index)].find("div", class_="an-text")['title'])


def select_subgroup_mikan(bangumi_id: int) -> tuple[int, str]:
    mikan_base_url = "https://mikanani.me/Home/Bangumi/"
    url = mikan_base_url + str(bangumi_id)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

    r = requests.get(url, headers=headers).text
    soup = BeautifulSoup(r, "html.parser")

    left_container = soup.select_one("div.pull-left.leftbar-container")
    title = left_container.find("p", class_="bangumi-title").text
    subgroup_list = left_container.select("ul.list-unstyled>li")
    for index, item in enumerate(subgroup_list):
        name = item.span.a.text
        print("########################")
        print(f"索引: {index}\n名称: {name}")
    chosen_index = input("输入选择字幕组的索引,如无匹配结果直接回车退出")
    if chosen_index == "":
        return (-1,"")
    subgroup_id = subgroup_list[int(chosen_index)].span.a['class'][-1].replace(
        "subgroup-", "")
    return (int(subgroup_id), subgroup_list[int(chosen_index)].span.a.text)


def analyze_rss(bangumi_id: int, subgroup_id: int,rule) -> tuple[str, dict]:
    mikan_base_url = "https://mikanani.me/RSS/Bangumi"
    params = {
        "bangumiId": str(bangumi_id),
        "subgroupid": str(subgroup_id)
    }
    r = requests.get(url=mikan_base_url, params=params)
    content = r.content
    result = feedparser.parse(content)

    title = result['feed']['title'][16:]

    map_title_to_torrent = {}
    for episode in result['entries']:
        for link in episode['links']:
            if link['type'] == 'application/x-bittorrent':
                if is_contented(episode['title'],rule):
                    map_title_to_torrent[episode['title']] = link['href']

    return (title, map_title_to_torrent)

def is_contented(vedio_title:str, rule:str):
    pattern = re.compile(rule)
    if len(re.findall(pattern,vedio_title)) >= 2 and (not "繁" in vedio_title):
        return True
    return False