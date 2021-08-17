import requests
import uuid
import json
from config.config import get_app_config
import logging
import threading


class Account(object):
    def __init__(self, username: str = None, password: str = None, client: str = None) -> None:
        self.accounts = {}
        self.lock = threading.Lock()
        self.app_config = get_app_config()
        self.base_url = self.app_config.config_dict["webserver_config"]["base_url"]
        self.session = requests.session()
        self.cookies = None
        if username is not None and password is not None and client is not None:
            self.login(user_name=username, password=password, client=client)
            self.accounts = self.get_account()

    def init_session(self):
        self.session.close()
        self.session = requests.session()

    def login(self, user_name: str, password: str, client: str = "") -> bool:
        login_url = self.base_url + "/user/login"
        hardware_info = self.get_hardware()
        data = {
            "hardware": hardware_info,
            "username": user_name,
            "password": password,
            "client": client
        }
        s = self.session
        try:
            login_res = s.post(url=login_url, data=data, timeout=1)
            if login_res.status_code == 200:
                login_res_data = json.loads(login_res.content)
                if login_res_data["code"] == 200:
                    self.cookies = s.cookies
                    return True
                else:
                    logging.warning("login failed")
                    return False
            else:
                logging.error("login connect rejected")
                return False
        except:
            logging.error("login timeout")
            return False

    def get_account(self) -> dict:
        get_account_url = self.base_url + "/account/get"
        s = self.session
        try:
            get_account_res = s.post(url=get_account_url, cookies=self.cookies)
            if get_account_res.status_code == 200:
                get_account_data = json.loads(get_account_res.content)
                if get_account_data["code"] == 200:
                    account_data = get_account_data["data"]["data"]
                else:
                    logging.warning("get account failed")
                    return {}
            else:
                logging.warning("get account connect rejected")
                return {}
        except:
            logging.error("get account timeout")
            return {}

        res = {}
        for account in account_data:
            modified_data = {}
            modified_data["account_id"]: str = str(account["id"])
            modified_data["counter_type"]: str = account["Counter"]["CounterType"]["Name"]
            modified_data["counter_version"]: str = account["Counter"]["CounterType"]["Version"]
            modified_data["trade_type"]: str = account["Counter"]["CounterType"]["Type"]
            modified_data["counter_detail"]: list = account["Counter"]["CounterDetail"]
            modified_data["account_detail"]: list = account["AccountDetail"]
            modified_data["conn_tes"]: bool = account["ConnectTES"]
            res[modified_data["account_id"]] = modified_data

        return res

    @staticmethod
    def get_mac_address() -> str:
        node = uuid.getnode()
        mac: str = uuid.UUID(int=node).hex[-12:]
        return mac.upper()

    def get_hardware(self) -> str:
        mac_address = self.get_mac_address()
        hardware_info = {"Network": {
            "Information": [{"MacAddress": mac_address}]}}
        res = str(json.dumps(hardware_info))
        return res


_account = None

def get_account(username: str = None, password: str = None, client: str = None) -> Account:
    global _account
    if not _account:
        _account = Account(username, password, client)
    return _account

if __name__ == '__main__':
    get_account("admin", "666666", "ots")