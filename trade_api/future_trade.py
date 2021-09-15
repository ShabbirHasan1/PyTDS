from trade_api.c_func import *
import logging
import os
from ctypes import *
from data.wrapper_data import get_api_pool, ApiInfo
from config.config import get_app_config, AppConfig
import threading
from queue import Queue
import copy

_final_status = {"F", "T", "C", "B", "R"}


class FutureTrade(object):
    def __init__(self, ftr_wrapper_path: str) -> None:
        self.ftr_wrapper = cdll.LoadLibrary(ftr_wrapper_path)
        redefine_ftr_trade_wrapper_func(self.ftr_wrapper)
        self.seq_num = 0
        self.api_pool = get_api_pool()

        self.order_data_lock = threading.Lock()
        self.order_data = {}
        self.trade_data_lock = threading.Lock()
        self.trade_data = []
        self.position_data_lock = threading.Lock()
        self.position_data = {}
        self.group_position_data = {}
        self.position_for_delta = {}

        self.seq_num_lock = threading.Lock()
        self.query_order_queue = Queue()
        self.query_trade_queue = Queue()
        self.query_position_queue = Queue()
        self.to_chase_order = {}
        self.to_chase_order_lock = threading.Lock()

        """init callbacks"""
        self.on_connected_cb = ftr_on_connected(self.on_connected)
        self.on_disconnected_cb = ftr_on_disconnected(self.on_disconnected)
        self.on_rsp_entrust_order_cb = ftr_on_rsp_entrust_order(
            self.on_rsp_entrust_order)
        self.on_rsp_cancel_order_cb = ftr_on_rsp_cancel_order(
            self.on_rsp_cancel_order)
        self.on_rsp_login_cb = ftr_on_rsp_login(self.on_rsp_login)
        self.on_rsp_logout_cb = ftr_on_rsp_logout(self.on_rsp_logout)
        self.on_ready_cb = ftr_on_ready(self.on_ready)
        self.on_rtn_order_cb = ftr_on_rtn_order(self.on_rtn_order)
        self.on_rtn_trade_cb = ftr_on_rtn_trade(self.on_rtn_trade)
        self.on_rsp_query_order_cb = ftr_on_rsp_query_order(self.on_rsp_query_order)
        self.on_rsp_query_trade_cb = ftr_on_rsp_query_trade(self.on_rsp_query_trade)
        self.on_rsp_query_capital_cb = ftr_on_rsp_query_capital(
            self.on_rsp_query_capital)
        self.on_rsp_query_position_cb = ftr_on_rsp_query_position(
            self.on_rsp_query_position)
        self.on_rsp_query_contract_cb = ftr_on_rsp_query_contract(
            self.on_rsp_query_contract)
        self.on_position_change_cb = ftr_on_position_change(self.on_position_change)

    def login_account(self, account_info: dict) -> None:
        api_config = self.ftr_wrapper.ftr_config_create()
        self.ftr_wrapper.ftr_config_set_account(api_config, account_info["account_id"].encode())
        app_config = get_app_config()
        self.set_api_config(api_config, account_info, app_config)

        err = STesError()

        ftr_api_t = self.ftr_wrapper.ftr_api_create(api_config, byref(err))
        if err.errid != 0:
            logging.error("创建api发生错误: " + str(get_data(err)))
            return
        logging.info("ftr_api_t created for account: {0}".format(account_info["account_id"]))

        self.set_api_callback(ftr_api_t)
        self.ftr_wrapper.ftr_api_initialize(ftr_api_t, byref(err))
        if err.errid != 0:
            logging.error("初始化api发生错误: " + str(get_data(err)))
            return
        logging.info("ftr_api_t initialized for account: {0}".format(account_info["account_id"]))

        self.ftr_wrapper.ftr_config_destroy(api_config)

        api_info = ApiInfo(account_id=account_info["account_id"], api_t=ftr_api_t, trade_type=1)
        self.api_pool.add_api_info(api_info)

    def set_api_config(self, api_config: int, account_info: dict, app_config: AppConfig) -> None:
        if account_info["conn_tes"]:
            # todo conn tes mode
            return
        else:
            account_id: str = account_info["account_id"]
            counter_name: str = account_info["counter_type"]
            counter_version: str = account_info["counter_version"]
            counter_detail: list = account_info["counter_detail"]
            account_detail: list = account_info["account_detail"]

            lib_path = app_config.driver_folder_path + "/" + counter_name + counter_version
            log_path = app_config.driver_log_path + "/" + counter_name + counter_version

            self.ftr_wrapper.ftr_config_set_driver(api_config, counter_name.encode())
            self.ftr_wrapper.ftr_config_set_version(api_config, counter_version.encode())
            self.ftr_wrapper.ftr_config_set_lib_path(api_config, lib_path.encode())
            self.ftr_wrapper.ftr_config_set_log_path(api_config, log_path.encode())

            for e in counter_detail:
                if e["Name"] == "CachePath":
                    cache_path = app_config.driver_cache_path
                    cur_account_cache_path = cache_path + "/" + account_id

                    if not os.path.exists(cur_account_cache_path):
                        try:
                            os.makedirs(cur_account_cache_path + e["Value"][1:])
                            logging.info("no cache folder, created")
                        except:
                            pass
                    e["Value"] = cur_account_cache_path + e["Value"][1:]

                self.ftr_wrapper.ftr_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())
            for e in account_detail:
                self.ftr_wrapper.ftr_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())

    def set_api_callback(self, ftr_api_t: int) -> None:
        self.ftr_wrapper.ftr_api_set_cb_connected(ftr_api_t, self.on_connected_cb)
        self.ftr_wrapper.ftr_api_set_cb_disconnected(ftr_api_t, self.on_disconnected_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_entrust_order(ftr_api_t, self.on_rsp_entrust_order_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_cancel_order(ftr_api_t, self.on_rsp_cancel_order_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_login(ftr_api_t, self.on_rsp_login_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_logout(ftr_api_t, self.on_rsp_logout_cb)
        self.ftr_wrapper.ftr_api_set_cb_ready(ftr_api_t, self.on_ready_cb)
        self.ftr_wrapper.ftr_api_set_cb_rtn_order(ftr_api_t, self.on_rtn_order_cb)
        self.ftr_wrapper.ftr_api_set_cb_rtn_trade(ftr_api_t, self.on_rtn_trade_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_query_order(ftr_api_t, self.on_rsp_query_order_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_query_trade(ftr_api_t, self.on_rsp_query_trade_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_query_capital(ftr_api_t, self.on_rsp_query_capital_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_query_position(ftr_api_t, self.on_rsp_query_position_cb)
        self.ftr_wrapper.ftr_api_set_cb_position_change(ftr_api_t, self.on_position_change_cb)
        self.ftr_wrapper.ftr_api_set_cb_rsp_query_contract(ftr_api_t, self.on_rsp_query_contract_cb)

    def entrust_order(self, order_info: dict) -> None:
        order_id = self.gen_seq_num()
        entrust = STesFtrEntrustOrder(
            account=order_info["account"].encode(),
            symbol=order_info["symbol"].encode(),
            exchange=order_info["exchange"].encode(),
            orderPriceType=order_info["orderPriceType"].encode(),
            direction=order_info["direction"].encode(),
            offset=order_info["offset"].encode(),
            hedgeFlag=order_info["hedgeFlag"],
            price=order_info["price"],
            volume=order_info["volume"],
            clientID=order_info["clientID"],
            orderID=order_id,
            trackCode=order_info["trackCode"].encode()
        )
        err = STesError()
        self.ftr_wrapper.ftr_api_entrust(order_info["api_t"], byref(entrust), order_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when entrust order, err msg: " + str(get_data(err)))

    def cancel_order(self, order_info: dict, chase_flag: bool = False) -> None:
        if chase_flag:
            self.to_chase_order_lock.acquire()
            self.to_chase_order[order_info["orderRef"]] = order_info
            self.to_chase_order_lock.release()
        to_cancel_order = STesFtrCancelOrder(
            orderRef=order_info["orderRef"].encode()
        )
        err = STesError()
        seq_id = self.gen_seq_num()
        self.ftr_wrapper.ftr_api_cancel(order_info["api_t"], byref(to_cancel_order), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when cancel order, err msg: " + str(get_data(err)))

    def query_order(self, api_t: int) -> None:
        err = STesError()
        seq_id = self.gen_seq_num()
        query = STesFtrQueryOrder()
        self.ftr_wrapper.ftr_api_query_orders(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query order, err msg: " + str(get_data(err)))

    def save_order(self, order: STesFtrOrder, ftr_api_t: int) -> None:
        order_data = get_data(order)
        order_data["api_t"] = ftr_api_t
        order_ref = order_data["orderRef"]
        self.order_data_lock.acquire()
        if order_ref in self.order_data and self.order_data[order_ref]["orderStatus"] in _final_status:
            logging.warning("order time sequence warning, orderRef: {0}".format(order_ref))
            self.order_data_lock.release()
            return

        self.order_data[order_ref] = order_data
        self.order_data_lock.release()
        # todo: chase order

    def get_order(self, order_ref: str) -> dict:
        self.order_data_lock.acquire()
        res = copy.deepcopy(self.order_data[order_ref])
        self.order_data_lock.release()
        return res

    def query_trade(self, api_t: int) -> None:
        err = STesError()
        query = STesFtrQueryTrade()
        seq_id = self.gen_seq_num()
        self.ftr_wrapper.ftr_api_query_trades(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query trade, err msg: " + str(get_data(err)))

    def save_trade(self, trade: STesFtrTrade) -> None:
        trade_data = get_data(trade)
        self.trade_data_lock.acquire()
        self.trade_data.append(trade_data)
        self.trade_data_lock.release()

    def query_position(self, api_t: int) -> None:
        err = STesError()
        query = STesFtrQueryPosition()
        seq_id = self.gen_seq_num()
        self.ftr_wrapper.ftr_api_query_positions(api_t, byref(query), seq_id, byref(err))

    def save_position(self, position: STesFtrPosition) -> None:
        position_data = get_data(position)
        key = position_data["account"], position_data["symbol"], position_data["posType"], position_data["hedgeFlag"]
        self.position_data_lock.acquire()

        # save default position
        self.position_data[key] = position_data

        # save grouped position
        if position_data["account"] not in self.group_position_data:
            self.group_position_data[position_data["account"]] = {}
        if position_data["symbol"] not in self.group_position_data[position_data["account"]]:
            self.group_position_data[position_data["account"]][position_data["symbol"]] = {}
        if position_data["hedgeFlag"] not in self.group_position_data[position_data["account"]][position_data["symbol"]]:
            self.group_position_data[position_data["account"]][position_data["symbol"]][position_data["hedgeFlag"]] = {}
        self.group_position_data[position_data["account"]][position_data["symbol"]][position_data["hedgeFlag"]][
            position_data["posType"]] = position_data

        # save position for delta
        product = position_data["symbol"][:2]
        if product != "IC" and product != "IF" and product != "IH":
            self.position_data_lock.release()
            return
        if position_data["account"] not in self.position_for_delta:
            self.position_for_delta[position_data["account"]] = {}
        if product not in self.position_for_delta[position_data["account"]]:
            self.position_for_delta[position_data["account"]][product] = {}
        if position_data["symbol"] not in self.position_for_delta[position_data["account"]][product]:
            self.position_for_delta[position_data["account"]][product][position_data["symbol"]] = {}
        self.position_for_delta[position_data["account"]][product][position_data["symbol"]][position_data["posType"]] = position_data

        self.position_data_lock.release()

    def get_position(self, key: tuple) -> dict:
        self.position_data_lock.acquire()
        res = copy.deepcopy(self.position_data[key])
        self.position_data_lock.release()
        return res

    def get_position_for_delta(self) -> dict:
        self.position_data_lock.acquire()
        res = copy.deepcopy(self.position_for_delta)
        self.position_data_lock.release()
        return res

    def gen_seq_num(self) -> int:
        self.seq_num_lock.acquire()
        self.seq_num += 1
        res = self.seq_num
        self.seq_num_lock.release()
        return res

    """回调函数"""

    @staticmethod
    def on_connected(ftr_api_t: int) -> None:
        api_pool = get_api_pool()
        api_pool.set_status_by_api(ftr_api_t, "connected")

        account_id = api_pool.get_api_info_by_api_t(ftr_api_t).get_account_id()
        logging.info("connect account {0} successfully".format(account_id))

        future_trade = get_future_trade()
        seq_id = future_trade.gen_seq_num()
        err = STesError()
        future_trade.ftr_wrapper.ftr_api_login(ftr_api_t, seq_id, byref(err))

    @staticmethod
    def on_disconnected(ftr_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rsp_login(ftr_api_t: int, rsp_login: POINTER(STesRspLogin), error: POINTER(STesError), req_id: int,
                     is_last: bool) -> None:
        err = error.contents
        # if is_last:
        if err.errid != 0:
            logging.warning("error occurred on login, err msg: " + str(get_data(err)))
            return
        rsp_login_data = rsp_login.contents
        client_id = rsp_login_data.clientID
        api_pool = get_api_pool()
        api_info = api_pool.get_api_info_by_api_t(ftr_api_t)
        api_info.update_client_id(client_id)
        api_info.update_status("login")

        account_id = api_info.get_account_id()
        logging.info("login account {0} successfully".format(account_id))

    @staticmethod
    def on_rsp_logout(ftr_api_t: int, rsp_logout: POINTER(STesRspLogout), error: POINTER(STesError), req_id: int,
                      is_last: bool) -> None:
        pass

    @staticmethod
    def on_ready(ftr_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        err = error.contents
        if err.errid != 0:
            logging.warning("error occurred on ready, err msg: " + str(get_data(err)))
            return
        future_trade = get_future_trade()
        future_trade.query_order(ftr_api_t)
        future_trade.query_trade(ftr_api_t)
        future_trade.query_position(ftr_api_t)

        api_pool = get_api_pool()
        api_pool.set_status_by_api(ftr_api_t, "ready")

        account_id = api_pool.get_api_info_by_api_t(ftr_api_t).get_account_id()
        logging.info("account {0} is ready".format(account_id))

    @staticmethod
    def on_req_error(ftr_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_error(ftr_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_entrust_order(ftr_api_t: int, entrust_order: POINTER(STesFtrEntrustOrder), error: POINTER(STesError),
                             req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_cancel_order(ftr_api_t: int, cancel_order: POINTER(STesFtrCancelOrder), error: POINTER(STesError),
                            req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_capital(ftr_api_t: int, capital: POINTER(STesFtrCapital), error: POINTER(STesError), req_id: int,
                             is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_contract(ftr_api_t: int, contract: POINTER(STesFtrContract), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_order(ftr_api_t: int, ftr_order: POINTER(STesFtrOrder), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(ftr_api_t).get_account_id()
            logging.warning("error on rsp query order for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_future_trade().save_order(ftr_order.contents, ftr_api_t)

    @staticmethod
    def on_rsp_query_trade(ftr_api_t: int, ftr_trade: POINTER(STesFtrTrade), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(ftr_api_t).get_account_id()
            logging.warning("error on rsp query trade for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_future_trade().save_trade(ftr_trade.contents)

    @staticmethod
    def on_rsp_query_position(ftr_api_t: int, ftr_position: POINTER(STesFtrPosition), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(ftr_api_t).get_account_id()
            logging.warning(
                "error on rsp query position for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_future_trade().save_position(ftr_position.contents)

    @staticmethod
    def on_rtn_error(ftr_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rtn_order(ftr_api_t: int, ftr_order: POINTER(STesFtrOrder)) -> None:
        get_future_trade().save_order(ftr_order.contents, ftr_api_t)

    @staticmethod
    def on_rtn_trade(ftr_api_t: int, ftr_trade: POINTER(STesFtrTrade)) -> None:
        get_future_trade().save_trade(ftr_trade.contents)

    @staticmethod
    def on_position_change(ftr_api_t: int, ftr_position: POINTER(STesFtrPosition)) -> None:
        get_future_trade().save_position(ftr_position.contents)


_future_trade = None


def get_future_trade() -> FutureTrade:
    global _future_trade
    if not _future_trade:
        app_config = get_app_config()
        _future_trade = FutureTrade(app_config.ftr_wrapper_path)
    return _future_trade
