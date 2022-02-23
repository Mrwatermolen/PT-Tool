# -*- coding: utf-8 -*-
from datetime import datetime
import sqlite3
import os

SUBSCRIBE_ACTION_INFO_MAP = [
    "default",  # 自动更新至最新剧集且追更 0
    "future",  # 仅追更 1
    "missing",  # 仅更新至最新剧集不订阅 2
]

SUBSCRIBE_ACTION_INDEX_MAP = {
    "default": 0,  # 自动更新至最新剧集且追更 0
    "future": 1,  # 仅追更 1
    "missing": 2  # 仅更新至最新剧集不订阅 2
}

SUBSCRIPTION_INDEX_MAP = {
    "id": 0,
    "bangumi_id": 1,
    "bangumi_name": 2,
    "media_name": 3,
    "subscribe_action": 4,
    "subgroup_id": 5,
    "subgroup_name": 6,
    "subgroup_priority": 7,
    "create_time": 8,
    "update_time": 9,
}

SUBSCRIPTION_INFO_MAP = {
    "id": "ID",
    "bangumi_id": "番剧ID",
    "bangumi_name": "番剧名",
    "media_name": "媒体名",
    "subscribe_action": "订阅动作",
    "subgroup_id": "字幕组ID",
    "subgroup_name": "字幕组名",
    "subgroup_priority": "字幕组优先级(0为最高)",
    "create_time": "订阅创建时间",
    "update_time": "订阅修改时间",
}


class SimpleToolSql():
    """
    SimpleToolSql for sqlite3
    """

    def __init__(self, file):
        """
        初始化数据库
        """
        self.file = file
        self.db = sqlite3.connect(self.file)
        self.c = self.db.cursor()

    def close(self):
        """
        关闭数据库
        """
        self.c.close()
        self.db.close()

    def execute(self, sql, param=None) -> bool:
        """
        执行数据库的增、删、改
        sql: sql语句
        param: 数据可以是list或tuple 亦可是None
        retutn: 成功返回True
        """
        try:
            if param is None:
                self.c.execute(sql)
            else:
                if type(param) is list:
                    self.c.executemany(sql, param)
                else:
                    self.c.execute(sql, param)
            count = self.db.total_changes
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)
            return False
        if count > 0:
            return True
        else:
            return False

    def query(self, sql, param=None) -> list:
        """
        查询语句
            sql:sql语句
            param:参数,可为None
            retutn:成功返回True
        """
        if param is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql, param)
        return self.c.fetchall()


class Manager(object):
    def __init__(self, config: dict):
        super(Manager, self).__init__()
        if not os.path.exists(config.get('database')):
            self.sql = SimpleToolSql(config.get('database'))
            self._create_db()
        else:
            self.sql = SimpleToolSql(config.get('database'))

    def _create_db(self):
        """
        我的订阅番剧表 subscription
            id: ID 唯一
            bangumi_id: 番剧的ID
            bangumi_name: 番剧名 由bangumi.tv查询获得或用户自定义
            media_name: jellfy可识别的剧集名称
            subscribe_action: 订阅动作 三种订阅动作由整数0 1 2标识
            subgroup_id: 字幕组ID
            subgroup_name: 字幕组名
            subgroup_priority: 字幕组优先级

        番剧集表 show
            id: ID 唯一
            bangumi_id: 该集所对应番剧的ID
            episode: 该集的集数
            subgroup_id: 对应来源字幕组ID
        """

        create_db_command = [
            '''CREATE TABLE subscription
                (id INTEGER PRIMARY KEY,
                bangumi_id  INTEGER,
                bangumi_name    TEXT,
                media_name  TEXT,
                subscribe_action    INTEGER,
                subgroup_id INTEGER,
                subgroup_name   TEXT,
                subgroup_priority   INTEGER,
                create_time TIMESTAMP,
                update_time TIMESTAMP);''',

            '''CREATE TABLE show
                (id INTEGER PRIMARY KEY,
                bangumi_id  INTEGER,
                episode  INTEGER,
                subgroup_id INTEGER,
                create_time TIMESTAMP,
                update_time TIMESTAMP);''',
        ]

        for command in create_db_command:
            self.sql.c.execute(command)

        return True

    def subscribe_bangumi(self, bangumi_id: int, bangumi_name: str, media_name: str, subscribe_action: int, subgroup_id: int, subgroup_name: str, subgroup_priority: int) -> bool:
        com_str = "INSERT INTO subscription values(?,?,?,?,?,?,?,?,?,?)"
        param = (None, bangumi_id, bangumi_name, media_name,
                 subscribe_action, subgroup_id, subgroup_name, subgroup_priority, datetime.now(), datetime.now())
        return self.sql.execute(com_str, param)

    def search_my_subscription(self, keywords: str = None, bangumi_id: int = None, subgroup_id: int = None) -> list:
        if not bangumi_id is None:
            res = self.sql.query(
                "select * from subscription where bangumi_id=?;", (bangumi_id,))
        elif not keywords is None:
            res = self.sql.query(
                "select * from SUBSCRIPTION where bangumi_name like '%"+keywords+"%'")
        else:
            res = self.sql.query("select * from SUBSCRIPTION;")
        return res

    def test_example(self):
        # 番剧订阅
        self.sql.execute("INSERT INTO subscription values(?,?,?,?,?,?,?)",
                         [(None, 2335, "进击的巨人 最终季", "Attack.on.Titan", 0, datetime.now(), datetime.now()),
                          (None, 2604, "鬼灭之刃", "Demon.Slayer.Kimetsu.no.Yaiba",
                             2, datetime.now(), datetime.now()),
                             (None, 26042, "进击的巨人F F最终季", "Attack.on.TitanFF", 1, datetime.now(), datetime.now())])

        self.sql.execute("UPDATE subscription set media_name = ?, update_time = ? where bangumi_id=?",
                         ("KKKKKK", datetime.now(), 2335))
