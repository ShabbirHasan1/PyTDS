import os
from pathlib import Path
import json
import logging


def get_cur_path() -> str:
    return os.path.dirname(__file__)


def get_parent_path(path: str) -> str:
    return os.path.dirname(path)


def transfer_path(path: str) -> str:
    return Path(path).as_posix()


class AppConfig(object):
    def __init__(self) -> None:
        cur_path = transfer_path(get_cur_path())
        self.src_path = transfer_path(get_parent_path(cur_path))
        self.resource_folder_path = transfer_path(os.path.join(self.src_path, "resource"))
        self.config_folder_path = transfer_path(os.path.join(self.resource_folder_path, "config"))

        self.driver_folder_path = transfer_path(os.path.join(self.resource_folder_path, "driver_wrapper"))
        self.driver_log_path = transfer_path(os.path.join(self.resource_folder_path, "driver_log"))
        self.driver_cache_path = transfer_path(os.path.join(self.resource_folder_path, "driver_cache"))

        self.trade_wrapper_path = transfer_path(os.path.join(self.resource_folder_path, "trade_wrapper"))
        self.opt_wrapper_path = transfer_path(os.path.join(self.trade_wrapper_path, "OptTradeWrapper_x64.dll"))
        self.ftr_wrapper_path = transfer_path(os.path.join(self.trade_wrapper_path, "FtrTradeWrapper_x64.dll"))
        self.stk_wrapper_path = transfer_path(os.path.join(self.trade_wrapper_path, "StkTradeWrapper_x64.dll"))

        self.config_dict = self.load_config()

    def load_config(self) -> dict:
        config_dict = {}
        config_path = transfer_path(os.path.join(self.config_folder_path, "config.json"))
        try:
            with open(config_path, "r") as f:
                config_dict = json.load(f)
            if not config_dict:
                logging.warning("config file is empty")
        except:
            logging.error("load config file failed")
        return config_dict


_app_config = None


def get_app_config() -> AppConfig:
    global _app_config
    if not _app_config:
        _app_config = AppConfig()
    return _app_config
