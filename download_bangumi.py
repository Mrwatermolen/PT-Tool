# -*- coding: utf-8 -*-
from transmission_rpc import Client


TORRENT_CLINET = {

}


class BtDownloader(object):
    def __init__(self, config: dict):
        super(BtDownloader, self).__init__()
        username = config.get('username')
        password = config.get('password')
        host = config.get('host')
        self.clinet = Client(
            username=username, password=password, host=host)

    def download_episode(self, torrent_url: str, save_path: str) -> int:
        """
        Return:
            torrent_id: int. -1 means failed
        """
        try:
            new_task = self.clinet.add_torrent(
                torrent=torrent_url, download_dir=save_path)
            torrent = self.clinet.get_torrent(torrent_id=new_task.id)
            torrent.seed_ratio_mode = "single"
            torrent.seed_ratio_limit = 2.0
            return new_task.id
        except BaseException as e:
            print(e)
            return -1
