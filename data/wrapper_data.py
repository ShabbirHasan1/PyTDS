import threading
import logging

class ApiInfo(object):
    # trade_type: 0 未指定， 1 期权， 2 期货， 3 现货
    def __init__(self, account_id: str = "", api_t: int = 0, client_id: int = 0, trade_type: int = 0) -> None:
        self.account_id = account_id
        self.api_t = api_t
        self.client_id = client_id
        self.trade_type = trade_type
        self.status = ""

    def update_account_id(self, account_id: str) -> None:
        if self.account_id:
            logging.warning("account_id is already in api info")
        self.account_id = account_id

    def update_api_t(self, api_t: int) -> None:
        if self.api_t:
            logging.warning("api_t is already in api info")
        self.api_t = api_t

    def update_client_id(self, client_id: int) -> None:
        if self.client_id:
            logging.warning("client_id is already in api info")
        self.client_id = client_id

    def update_status(self, status: str) -> None:
        self.status = status

    def get_account_id(self) -> str:
        return self.account_id

    def get_api_t(self) -> int:
        return self.api_t

    def get_client_id(self) -> int:
        return self.client_id

    def get_status(self) -> str:
        return self.status

class ApiPool(object):
    def __init__(self) -> None:
        self.api_pool = set()
        self.account_dict = {}
        self.api_dict = {}
        self.client_id_dict = {}
        self.lock = threading.Lock()

    def add_api_info(self, api: ApiInfo) -> None:
        self.lock.acquire()
        self.api_pool.add(api)
        self.account_dict[api.account_id] = api
        self.api_dict[api.api_t] = api
        self.client_id_dict[api.client_id] = api
        self.lock.release()

    def get_api_info_by_account(self, account_id: str) -> ApiInfo or None:
        self.lock.acquire()
        if account_id in self.account_dict:
            self.lock.release()
            return self.account_dict[account_id]
        self.lock.release()
        logging.warning("cannot find api info by account id: {0}".format(account_id))
        return None

    def get_api_info_by_api_t(self, api_t: int) -> ApiInfo or None:
        self.lock.acquire()
        if api_t in self.api_dict:
            self.lock.release()
            return self.api_dict[api_t]
        self.lock.release()
        logging.warning("cannot find api info by api_t: {0}".format(api_t))
        return None

    def get_api_info_by_client_id(self, client_id: int) -> ApiInfo or None:
        self.lock.acquire()
        if client_id in self.client_id_dict:
            self.lock.release()
            return self.client_id_dict[client_id]
        self.lock.release()
        logging.warning("cannot find api info by client id: {0}".format(client_id))
        return None

    def remove_api_info_by_account(self, account_id: int) -> bool:
        self.lock.acquire()
        if account_id in self.account_dict:
            api_info: ApiInfo = self.account_dict[account_id]
            self.account_dict.pop(account_id)
            self.api_dict.pop(api_info.api_t)
            self.client_id_dict.pop(api_info.client_id)
            self.api_pool.remove(api_info)
            self.lock.release()
            return True
        else:
            self.lock.release()
            logging.warning("cannot find api info for account {0}".format(account_id))
            return False

    def set_status_by_api(self, api_t: int, status: int) -> None:
        self.lock.acquire()
        if api_t not in self.api_dict:
            logging.warning("cannot find api info by api_t: {0}".format(api_t))
            self.lock.release()
            return
        self.api_dict[api_t].update_status(status)
        self.lock.release()

_api_pool = None

def get_api_pool():
    global _api_pool
    if not _api_pool:
        _api_pool = ApiPool()
    return _api_pool