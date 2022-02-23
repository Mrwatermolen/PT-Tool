# -*- coding: utf-8 -*-
import argparse
import os
import re


parser = argparse.ArgumentParser(description='硬链文件至媒体库中,并重命名文件')

parser.add_argument('--src', type=str, help='源文件/文件夹所在路径')
parser.add_argument('--n', type=str, help='源文件/文件夹名')
parser.add_argument('--dst', type=str, help='硬链接的路径')
parser.add_argument("--r", type=str, help="正则表达式")
args = parser.parse_args()


def hard_link(src, dst, name):
    try:
        if os.path.exists(src):
            if os.path.exists(dst):
                os.mkdir(dst)
            if os.path.isdir(src):
                print(1)
            else:
                os.link(src=src, dst=dst)
    except BaseException as e:
        print(e)


def rename_file(save_path: str, file_name: str, regex: str, prefix_name):
    """
    多数番剧的命名可抽象为: "str1"+"集数"+"str2"+"后缀名"
    其中"str1"修改为: "剧集名"+"季数","str2"删除。由此jellyfin即可识别番剧
    例子: 
        "[NC-Raws] 进击的巨人 The Final Season / Kyojin F Part 2 - 20 (Baha 1920x1080 AVC AAC MP4)[481.99 MB].mp4"
        可刮削识别的名称: "Attack.on.Titan.S04E20.mp4"
    备注: 多季播放的番剧,某些组的剧集集数是连着前面的季度的集数来计算的。即比如某部番剧第一季为12集,而S02E01可能会是E13。
    Args:
        save_path: 文件保存路径
        file_name: 文件名
        regex: Subject Type.
        prefix_name: Query page
    """
    old = os.path.join(save_path, file_name)
    if not os.path.exists(old):
        raise FileNotFoundError(f"{old} 文件不存在")

    pattern_prefix = re.compile(regex)
    pattern_protect_suffix = re.compile(r'(.mp4|.mkv)*$')
    pattern_get_number_len = re.compile(r'[0-9]+')

    (prefix_start, prefix_end) = pattern_prefix.search(file_name).regs[0]
    suffix_start = pattern_protect_suffix.search(file_name).regs[0][0]
    (number_start, number_end) = pattern_get_number_len.search(
        file_name[prefix_start:prefix_end]).regs[0]
    number_len = number_end - number_start

    new_name = file_name.replace(file_name[prefix_end:suffix_start], "")
    new_name = new_name.replace(
        new_name[:prefix_end - number_len], prefix_name)
    print(file_name)
    print(new_name)

    new = os.path.join(save_path, new_name)
    os.rename(old, new)
