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


class StockTrade(object):
    def __init__(self, stk_wrapper_path: str) -> None:
        self.stk_wrapper = cdll.LoadLibrary(stk_wrapper_path)
        redefine_stk_trade_wrapper_func(self.stk_wrapper)
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
        self.on_connected_cb = stk_on_connected(self.on_connected)
        self.on_disconnected_cb = stk_on_disconnected(self.on_disconnected)
        self.on_rsp_entrust_order_cb = stk_on_rsp_entrust_order(
            self.on_rsp_entrust_order)
        self.on_rsp_cancel_order_cb = stk_on_rsp_cancel_order(
            self.on_rsp_cancel_order)
        self.on_rsp_login_cb = stk_on_rsp_login(self.on_rsp_login)
        self.on_rsp_logout_cb = stk_on_rsp_logout(self.on_rsp_logout)
        self.on_ready_cb = stk_on_ready(self.on_ready)
        self.on_rtn_order_cb = stk_on_rtn_order(self.on_rtn_order)
        self.on_rtn_trade_cb = stk_on_rtn_trade(self.on_rtn_trade)
        self.on_rsp_query_order_cb = stk_on_rsp_query_order(self.on_rsp_query_order)
        self.on_rsp_query_trade_cb = stk_on_rsp_query_trade(self.on_rsp_query_trade)
        self.on_rsp_query_capital_cb = stk_on_rsp_query_capital(
            self.on_rsp_query_capital)
        self.on_rsp_query_position_cb = stk_on_rsp_query_position(
            self.on_rsp_query_position)
        self.on_rsp_query_contract_cb = stk_on_rsp_query_contract(
            self.on_rsp_query_contract)
        self.on_position_change_cb = stk_on_position_change(self.on_position_change)

    def login_account(self, account_info: dict) -> None:
        api_config = self.stk_wrapper.stk_config_create()
        self.stk_wrapper.stk_config_set_account(api_config, account_info["account_id"].encode())
        app_config = get_app_config()
        self.set_api_config(api_config, account_info, app_config)

        err = STesError()

        stk_api_t = self.stk_wrapper.stk_api_create(api_config, byref(err))
        if err.errid != 0:
            logging.error("创建api发生错误: " + str(get_data(err)))
            return
        logging.info("stk_api_t created for account: {0}".format(account_info["account_id"]))

        self.set_api_callback(stk_api_t)
        self.stk_wrapper.stk_api_initialize(stk_api_t, byref(err))
        if err.errid != 0:
            logging.error("初始化api发生错误: " + str(get_data(err)))
            return
        logging.info("stk_api_t initialized for account: {0}".format(account_info["account_id"]))

        self.stk_wrapper.stk_config_destroy(api_config)

        api_info = ApiInfo(account_id=account_info["account_id"], api_t=stk_api_t, trade_type=1)
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

            self.stk_wrapper.stk_config_set_driver(api_config, counter_name.encode())
            self.stk_wrapper.stk_config_set_version(api_config, counter_version.encode())
            self.stk_wrapper.stk_config_set_lib_path(api_config, lib_path.encode())
            self.stk_wrapper.stk_config_set_log_path(api_config, log_path.encode())

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

                self.stk_wrapper.stk_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())
            for e in account_detail:
                self.stk_wrapper.stk_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())

    def set_api_callback(self, stk_api_t: int) -> None:
        self.stk_wrapper.stk_api_set_cb_connected(stk_api_t, self.on_connected_cb)
        self.stk_wrapper.stk_api_set_cb_disconnected(stk_api_t, self.on_disconnected_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_entrust_order(stk_api_t, self.on_rsp_entrust_order_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_cancel_order(stk_api_t, self.on_rsp_cancel_order_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_login(stk_api_t, self.on_rsp_login_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_logout(stk_api_t, self.on_rsp_logout_cb)
        self.stk_wrapper.stk_api_set_cb_ready(stk_api_t, self.on_ready_cb)
        self.stk_wrapper.stk_api_set_cb_rtn_order(stk_api_t, self.on_rtn_order_cb)
        self.stk_wrapper.stk_api_set_cb_rtn_trade(stk_api_t, self.on_rtn_trade_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_query_order(stk_api_t, self.on_rsp_query_order_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_query_trade(stk_api_t, self.on_rsp_query_trade_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_query_capital(stk_api_t, self.on_rsp_query_capital_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_query_position(stk_api_t, self.on_rsp_query_position_cb)
        self.stk_wrapper.stk_api_set_cb_position_change(stk_api_t, self.on_position_change_cb)
        self.stk_wrapper.stk_api_set_cb_rsp_query_contract(stk_api_t, self.on_rsp_query_contract_cb)

    def entrust_order(self, order_info: dict) -> None:
        order_id = self.gen_seq_num()
        entrust = STesStkEntrustOrder(
            account=order_info["account"].encode(),
            symbol=order_info["symbol"].encode(),
            exchange=order_info["exchange"].encode(),
            orderPriceType=order_info["orderPriceType"].encode(),
            direction=order_info["direction"].encode(),
            offset=order_info["offset"].encode(),
            hedgeFlag=order_info["hedgeFlag"].encode(),
            price=order_info["price"],
            volume=order_info["volume"],
            clientID=order_info["clientID"],
            orderID=order_id,
            tradeCode=order_info["trackCode"]
        )
        err = STesError()
        self.stk_wrapper.stk_api_entrust(order_info["api_t"], byref(entrust), order_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when entrust order, err msg: " + str(get_data(err)))

    def cancel_order(self, order_info: dict, chase_flag: bool = False) -> None:
        if chase_flag:
            self.to_chase_order_lock.acquire()
            self.to_chase_order[order_info["orderRef"]] = order_info
            self.to_chase_order_lock.release()
        to_cancel_order = STesStkCancelOrder(
            orderRef=order_info["orderRef"].encode()
        )
        err = STesError()
        seq_id = self.gen_seq_num()
        self.stk_wrapper.stk_api_cancel(order_info["api_t"], byref(to_cancel_order), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when cancel order, err msg: " + str(get_data(err)))

    def query_order(self, api_t: int) -> None:
        err = STesError()
        seq_id = self.gen_seq_num()
        query = STesStkQueryOrder()
        self.stk_wrapper.stk_api_query_orders(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query order, err msg: " + str(get_data(err)))

    def save_order(self, order: STesStkOrder, stk_api_t: int) -> None:
        order_data = get_data(order)
        order_data["api_t"] = stk_api_t
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
        query = STesStkQueryTrade()
        seq_id = self.gen_seq_num()
        self.stk_wrapper.stk_api_query_trades(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query trade, err msg: " + str(get_data(err)))

    def save_trade(self, trade: STesStkTrade) -> None:
        trade_data = get_data(trade)
        self.trade_data_lock.acquire()
        self.trade_data.append(trade_data)
        self.trade_data_lock.release()

    def query_position(self, api_t: int) -> None:
        err = STesError()
        query = STesStkQueryPosition()
        seq_id = self.gen_seq_num()
        self.stk_wrapper.stk_api_query_positions(api_t, byref(query), seq_id, byref(err))

    def save_position(self, position: STesStkPosition) -> None:
        position_data = get_data(position)
        key = position_data["account"], position_data["symbol"]
        self.position_data_lock.acquire()

        # save default position
        self.position_data[key] = position_data

        # save grouped position
        if position_data["account"] not in self.group_position_data:
            self.group_position_data[position_data["account"]] = {}
        self.group_position_data[position_data["account"]][position_data["symbol"]] = position_data

        # save position for delta
        if position_data["account"] not in self.position_for_delta:
            self.position_for_delta[position_data["account"]] = {}
        if position_data["symbol"] == "510050" or position_data["symbol"] == "510300" or position_data["symbol"] == "159919":
            self.position_for_delta[position_data["account"]][position_data["symbol"]] = position_data
        else:
            self.position_data_lock.release()
            return

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
    def on_connected(stk_api_t: int) -> None:
        api_pool = get_api_pool()
        api_pool.set_status_by_api(stk_api_t, "connected")

        account_id = api_pool.get_api_info_by_api_t(stk_api_t).get_account_id()
        logging.info("connect account {0} successfully".format(account_id))

        stock_trade = get_stock_trade()
        seq_id = stock_trade.gen_seq_num()
        err = STesError()
        stock_trade.stk_wrapper.stk_api_login(stk_api_t, seq_id, byref(err))

    @staticmethod
    def on_disconnected(stk_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rsp_login(stk_api_t: int, rsp_login: POINTER(STesRspLogin), error: POINTER(STesError), req_id: int,
                     is_last: bool) -> None:
        err = error.contents
        # if is_last:
        if err.errid != 0:
            logging.warning("error occurred on login, err msg: " + str(get_data(err)))
            return
        rsp_login_data = rsp_login.contents
        client_id = rsp_login_data.clientID
        api_pool = get_api_pool()
        api_info = api_pool.get_api_info_by_api_t(stk_api_t)
        api_info.update_client_id(client_id)
        api_info.update_status("login")

        account_id = api_info.get_account_id()
        logging.info("login account {0} successfully".format(account_id))

    @staticmethod
    def on_rsp_logout(stk_api_t: int, rsp_logout: POINTER(STesRspLogout), error: POINTER(STesError), req_id: int,
                      is_last: bool) -> None:
        pass

    @staticmethod
    def on_ready(stk_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        err = error.contents
        if err.errid != 0:
            logging.warning("error occurred on ready, err msg: " + str(get_data(err)))
            return
        stock_trade = get_stock_trade()
        stock_trade.query_order(stk_api_t)
        stock_trade.query_trade(stk_api_t)
        stock_trade.query_position(stk_api_t)

        api_pool = get_api_pool()
        api_pool.set_status_by_api(stk_api_t, "ready")

        account_id = api_pool.get_api_info_by_api_t(stk_api_t).get_account_id()
        logging.info("account {0} is ready".format(account_id))

    @staticmethod
    def on_req_error(stk_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_error(stk_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_entrust_order(stk_api_t: int, entrust_order: POINTER(STesStkEntrustOrder), error: POINTER(STesError),
                             req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_cancel_order(stk_api_t: int, cancel_order: POINTER(STesStkCancelOrder), error: POINTER(STesError),
                            req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_capital(stk_api_t: int, capital: POINTER(STesStkCapital), error: POINTER(STesError), req_id: int,
                             is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_contract(stk_api_t: int, contract: POINTER(STesStkContract), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_order(stk_api_t: int, stk_order: POINTER(STesStkOrder), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(stk_api_t).get_account_id()
            logging.warning("error on rsp query order for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_stock_trade().save_order(stk_order.contents, stk_api_t)

    @staticmethod
    def on_rsp_query_trade(stk_api_t: int, stk_trade: POINTER(STesStkTrade), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(stk_api_t).get_account_id()
            logging.warning("error on rsp query trade for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_stock_trade().save_trade(stk_trade.contents)

    @staticmethod
    def on_rsp_query_position(stk_api_t: int, stk_position: POINTER(STesStkPosition), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(stk_api_t).get_account_id()
            logging.warning(
                "error on rsp query position for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_stock_trade().save_position(stk_position.contents)

    @staticmethod
    def on_rtn_error(stk_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rtn_order(stk_api_t: int, stk_order: POINTER(STesStkOrder)) -> None:
        get_stock_trade().save_order(stk_order.contents, stk_api_t)

    @staticmethod
    def on_rtn_trade(stk_api_t: int, stk_trade: POINTER(STesStkTrade)) -> None:
        get_stock_trade().save_trade(stk_trade.contents)

    @staticmethod
    def on_position_change(stk_api_t: int, stk_position: POINTER(STesStkPosition)) -> None:
        get_stock_trade().save_position(stk_position.contents)


_stock_trade = None


def get_stock_trade() -> StockTrade:
    global _stock_trade
    if not _stock_trade:
        app_config = get_app_config()
        _stock_trade = StockTrade(app_config.stk_wrapper_path)
    return _stock_trade
