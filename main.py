# -*- coding: utf-8 -*-
from bangumi_source import search_bangumi_mikan, select_subgroup_mikan, analyze_rss
from download_bangumi import BtDownloader
from manager import Manager, SUBSCRIPTION_INDEX_MAP, SUBSCRIPTION_INFO_MAP

import re
import yaml
import os
import bisect

APP_CONFIG = {}

SHOW_TEMPLATE = ["bangumi_name", "media_name", "subscribe_action",
                 "subgroup_name", "subgroup_priority", "create_time", "update_time"]


def print_subscription(data: list):
    info = ""
    for item in SHOW_TEMPLATE:
        info = info + \
            f" {SUBSCRIPTION_INFO_MAP[item]}: {data[SUBSCRIPTION_INDEX_MAP[item]]}"
    print(info)


def subscribe_bangumi(rule: str, keywords: str = None, bangumi_id: int = None, subgroup_id: int = None) -> bool:
    res = lib_manager.search_my_subscription(
        keywords=keywords, bangumi_id=bangumi_id, subgroup_id=subgroup_id)
    flag = ""

    if not keywords is None:
        # 首先搜索本地资料库是否存在
        print(f"关键词:{keywords} 查询结果: {len(res)}条")
        for data in res:
            print_subscription(data)

        flag = input(f"是否进入订阅,输入1确认")
        if flag == "1":
            # 在Mikan上搜索番剧
            print("正在进入订阅 开始搜索番剧")
            (bangumi_id, bangumi_name) = search_bangumi_mikan(
                bangumi_keywords=keywords)
            if bangumi_id != -1:
                # 成功选择番剧后 再从本地资料库中搜索选择的番剧是否存在
                res = lib_manager.search_my_subscription(bangumi_id=bangumi_id)
                print(f"番剧:{bangumi_name} 在本地资料库的查询结果: {len(res)}条")
                for data in res:
                    print_subscription(data)
                flag = input("是否继续订阅 输入1确认\n")
                print("开始搜索字幕组")
                (subgroup_id, subgroup_name) = select_subgroup_mikan(
                    bangumi_id=bangumi_id)
                if subgroup_id != -1:
                    # 成功选择发布源后 再从本地资料库中搜索选择的番剧的对应发布源是否存在
                    for data in res:
                        if data[SUBSCRIPTION_INDEX_MAP["subgroup_id"]] == subgroup_id:
                            print("发布源已经存在")
                            # 接下来打印信息 转到修改订阅
                            flag = input("是否修改该订阅 输入1确认 其他推出该番剧的订阅\n")
                            if flag == "1":
                                return

                    print("开始分析发布源")
                    res = analyze_rss(bangumi_id=bangumi_id,
                                      subgroup_id=subgroup_id, rule=rule)
                    bangumi_name = res[0]
                    # for i in original_name_to_media_name(res[1],1,"2"):
                    #     print(i)
                    for i in res[1]:
                        print(i)
                    flag = ""
                    flag = input(
                        f"是否确认订阅{bangumi_name}, 源: {subgroup_name}\n输入1确认")
                    if flag == "1":
                        print("选择参数输入")
                        media_name = input("TMDB\n")
                        subscribe_action = int(input("订阅动作\n"))
                        subgroup_priority = int(input("字幕组优先级\n"))
                        if (lib_manager.subscribe_bangumi(bangumi_id, bangumi_name, media_name, subscribe_action, subgroup_id, subgroup_name, subgroup_priority)):
                            print("订阅成功! ")
                            return True
                        else:
                            print("向数据库中添加数据错误! 尝试保存到本地!")
    return False


def compare_subgroup_source_with_local(sub_sourec: list[str], local_media: dict = None, offset:int = 0):
    if local_media:
        can_fix = []
        pattern = re.compile(r'\[[0-9]+\]')  # 用于匹配剧集数为 [剧集数] 会忽略例如 [08v2]
        episodes = get_episode_from_original_name(sub_sourec, pattern)
        sorted(episodes)
        episodes[:] = [x - offset for x in episodes]
        for i in local_media["missing"]:
            is_fix = bisect.bisect_left(episodes,i)
            if is_fix != len(episodes) and episodes[is_fix] == i:
                can_fix.append(i)
        if can_fix == local_media["missing"]:
            print("此源能补全缺少的所有剧集")
    else:
        print("无本地媒体库")


def original_name_to_media_name(original_names: list[str], start_index: int, media_name: str) -> list[str]:
    """
    多数番剧的命名可抽象为: "str1"+"集数"+"str2"+"后缀名"
    其中"str1"修改为: "剧集名"+"季数","str2"删除。由此jellyfin即可识别番剧
    例子: 
        "[NC-Raws] 进击的巨人 The Final Season / Kyojin F Part 2 - 20 (Baha 1920x1080 AVC AAC MP4)[481.99 MB].mp4"
        可刮削识别的名称: "Attack.on.Titan.S04E20.mp4"
    备注: 多季播放的番剧,某些组的剧集集数是连着前面的季度的集数来计算的。即比如某部番剧第一季为12集,而S02E01可能会是E13。
    Args:
        original_names: 文件保存路径
        file_name: 文件名
        regex: Subject Type.
        prefix_name: Query page
    """
    new_names = []
    pattern = re.compile(r'\[[0-9]+\]')  # 用于匹配剧集数为 [剧集数] 会忽略例如 [08v2]
    episodes = get_episode_from_original_name(original_names, pattern)
    for episode in episodes:
        episode = episode - start_index
        if episode <= 0:
            continue
        new_names.append(media_name + "E" + str(episode))
    return new_names


def get_episode_from_original_name(original_names: list[str], pattern: re.Pattern) -> list[int]:
    episodes = []
    for name in original_names:
        if pattern.search(name):
            (start, end) = pattern.search(name).regs[0]
            episode = name[start+1:end-1]
            episode = int(episode)
            episode.append(episode)
    return episodes


def concatenation_str_to_media_name():
    pass


def edit_subscription():
    pass


def get_local_show_info(media_library_path: str, media_name: str = ""):
    episode_list = []
    if os.path.exists(media_library_path):
        for root, dirs, names in os.walk(media_library_path):
            for name in names:
                ext_name = os.path.splitext(name)[1]
                if ".mp4" in ext_name or ".mkv" in ext_name:
                    episode_list.append(name)
    if episode_list == []:
        print("本地无资源")
    else:
        print(get_episode_from_local(episode_list, media_name))


def get_episode_from_local(episode_list: list[str], media_name: str = "") -> dict:
    episode_pattern = re.compile("E[0-9]+")
    data = {
        "haved": [],
        "missing": []
    }
    for name in episode_list:
        name = name.replace(media_name, "")
        (start, end) = episode_pattern.search(name).regs[0]
        data["haved"].append(int(name[start+1:end]))
    sorted(data["haved"])

    end = data["haved"][-1]
    temp = [0] * end
    for i in data["haved"]:
        temp[i - 1] = 1
    for i in range(end):
        if not temp[i]:
            data["missing"].append(i+1)

    return data


def progress_scan_media(media_library_path: str, media_name: str):
    get_local_show_info(media_library_path)


if __name__ == "__main__":
    pwd = os.path.dirname(os.path.realpath(__file__))
    configPath = os.path.join(pwd, "config.yaml")

    try:
        with open(configPath, 'r', encoding='utf-8') as f:
            APP_CONFIG = yaml.safe_load(f)
            print(APP_CONFIG)
            rule = APP_CONFIG["vedio_quality"]
            media_library_path = APP_CONFIG["media_library_path"]
        get_local_show_info(media_library_path, media_name="")
        lib_manager = Manager(config=APP_CONFIG)
        # downloader = BtDownloader(config=APP_CONFIG['downloader'])
        # lib_manager.test_example()

        # while True:
        #     x = input("查找的番剧\n")
        #     if subscribe_bangumi(keywords=x, rule=rule):
        #         print("正在匹配本地资源")

        test_sample = []
        with open("r.txt", "r", encoding="utf-8") as f:
            test_sample = f.readlines()
        new_p = original_name_to_media_name(
            test_sample, 59, "Attack.on.Titan.S04")
        for i in new_p:
            print(i)

    except BaseException as e:
        print(e)
