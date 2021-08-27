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


class OptionTrade(object):
    def __init__(self, opt_wrapper_path: str) -> None:
        self.opt_wrapper = cdll.LoadLibrary(opt_wrapper_path)
        redefine_opt_trade_wrapper_func(self.opt_wrapper)
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
        self.on_connected_cb = opt_on_connected(self.on_connected)
        self.on_disconnected_cb = opt_on_disconnected(self.on_disconnected)
        self.on_rsp_entrust_order_cb = opt_on_rsp_entrust_order(
            self.on_rsp_entrust_order)
        self.on_rsp_cancel_order_cb = opt_on_rsp_cancel_order(
            self.on_rsp_cancel_order)
        self.on_rsp_login_cb = opt_on_rsp_login(self.on_rsp_login)
        self.on_rsp_logout_cb = opt_on_rsp_logout(self.on_rsp_logout)
        self.on_ready_cb = opt_on_ready(self.on_ready)
        self.on_rtn_order_cb = opt_on_rtn_order(self.on_rtn_order)
        self.on_rtn_trade_cb = opt_on_rtn_trade(self.on_rtn_trade)
        self.on_rsp_query_order_cb = opt_on_rsp_query_order(self.on_rsp_query_order)
        self.on_rsp_query_trade_cb = opt_on_rsp_query_trade(self.on_rsp_query_trade)
        self.on_rsp_query_capital_cb = opt_on_rsp_query_capital(
            self.on_rsp_query_capital)
        self.on_rsp_query_position_cb = opt_on_rsp_query_position(
            self.on_rsp_query_position)
        self.on_rsp_query_contract_cb = opt_on_rsp_query_contract(
            self.on_rsp_query_contract)
        self.on_position_change_cb = opt_on_position_change(self.on_position_change)

        # 备兑相关
        self.on_rsp_covered_lock_cb = opt_on_rsp_covered_lock(
            self.on_rsp_covered_lock)
        self.on_rsp_query_lock_order_cb = opt_on_rsp_query_lock_order(
            self.on_rsp_query_lock_order)
        self.on_rsp_query_lock_position_cb = opt_on_rsp_query_lock_position(
            self.on_rsp_query_lock_position)
        self.on_rtn_lock_cb = opt_on_rtn_lock(self.on_rtn_lock)
        self.on_lock_position_change_cb = opt_on_lock_position_change(
            self.on_lock_position_change)

        # 行权相关
        self.on_rsp_entrust_exec_order_cb = opt_on_rsp_entrust_exec_order(
            self.on_rsp_entrust_exec_order)
        self.on_rsp_cancel_exec_order_cb = opt_on_rsp_cancel_exec_order(
            self.on_rsp_cancel_exec_order)
        self.on_rsp_query_exec_order_cb = opt_on_rsp_query_exec_order(
            self.on_rsp_query_exec_order)
        self.on_rtn_exec_order_cb = opt_on_rtn_exec_order(self.on_rtn_exec_order)

    def login_account(self, account_info: dict) -> None:
        api_config = self.opt_wrapper.opt_config_create()
        self.opt_wrapper.opt_config_set_account(api_config, account_info["account_id"].encode())
        app_config = get_app_config()
        self.set_api_config(api_config, account_info, app_config)

        err = STesError()

        opt_api_t = self.opt_wrapper.opt_api_create(api_config, byref(err))
        if err.errid != 0:
            logging.error("创建api发生错误: " + str(get_data(err)))
            return
        logging.info("opt_api_t created for account: {0}".format(account_info["account_id"]))

        self.set_api_callback(opt_api_t)
        self.opt_wrapper.opt_api_initialize(opt_api_t, byref(err))
        if err.errid != 0:
            logging.error("初始化api发生错误: " + str(get_data(err)))
            return
        logging.info("opt_api_t initialized for account: {0}".format(account_info["account_id"]))

        self.opt_wrapper.opt_config_destroy(api_config)

        api_info = ApiInfo(account_id=account_info["account_id"], api_t=opt_api_t, trade_type=1)
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

            self.opt_wrapper.opt_config_set_driver(api_config, counter_name.encode())
            self.opt_wrapper.opt_config_set_version(api_config, counter_version.encode())
            self.opt_wrapper.opt_config_set_lib_path(api_config, lib_path.encode())
            self.opt_wrapper.opt_config_set_log_path(api_config, log_path.encode())

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

                self.opt_wrapper.opt_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())
            for e in account_detail:
                self.opt_wrapper.opt_config_set_attribute(api_config, e["Name"].encode(), e["Value"].encode())

    def set_api_callback(self, opt_api_t: int) -> None:
        self.opt_wrapper.opt_api_set_cb_connected(opt_api_t, self.on_connected_cb)
        self.opt_wrapper.opt_api_set_cb_disconnected(opt_api_t, self.on_disconnected_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_entrust_order(opt_api_t, self.on_rsp_entrust_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_cancel_order(opt_api_t, self.on_rsp_cancel_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_login(opt_api_t, self.on_rsp_login_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_logout(opt_api_t, self.on_rsp_logout_cb)
        self.opt_wrapper.opt_api_set_cb_ready(opt_api_t, self.on_ready_cb)
        self.opt_wrapper.opt_api_set_cb_rtn_order(opt_api_t, self.on_rtn_order_cb)
        self.opt_wrapper.opt_api_set_cb_rtn_trade(opt_api_t, self.on_rtn_trade_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_order(opt_api_t, self.on_rsp_query_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_trade(opt_api_t, self.on_rsp_query_trade_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_capital(opt_api_t, self.on_rsp_query_capital_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_position(opt_api_t, self.on_rsp_query_position_cb)
        self.opt_wrapper.opt_api_set_cb_position_change(opt_api_t, self.on_position_change_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_contract(opt_api_t, self.on_rsp_query_contract_cb)
        """备兑相关"""
        self.opt_wrapper.opt_api_set_cb_rsp_covered_lock(opt_api_t, self.on_rsp_covered_lock_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_lock_order(opt_api_t, self.on_rsp_query_lock_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_lock_position(opt_api_t, self.on_rsp_query_lock_position_cb)
        self.opt_wrapper.opt_api_set_cb_rtn_lock(opt_api_t, self.on_rtn_lock_cb)
        self.opt_wrapper.opt_api_set_cb_lock_position_change(opt_api_t, self.on_lock_position_change_cb)
        """行权相关"""
        self.opt_wrapper.opt_api_set_cb_rsp_entrust_exec_order(opt_api_t, self.on_rsp_entrust_exec_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_cancel_exec_order(opt_api_t, self.on_rsp_cancel_exec_order_cb)
        self.opt_wrapper.opt_api_set_cb_rsp_query_exec_order(opt_api_t, self.on_rsp_query_exec_order_cb)
        self.opt_wrapper.opt_api_set_cb_rtn_exec_order(opt_api_t, self.on_rtn_exec_order_cb)

    def entrust_order(self, order_info: dict) -> None:
        order_id = self.gen_seq_num()
        entrust = STesOptEntrustOrder(
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
            tradeCode=order_info["trackCode"].decode()
        )
        err = STesError()
        self.opt_wrapper.opt_api_entrust(order_info["api_t"], byref(entrust), order_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when entrust order, err msg: " + str(get_data(err)))

    def cancel_order(self, order_info: dict, chase_flag: bool = False) -> None:
        if chase_flag:
            self.to_chase_order_lock.acquire()
            self.to_chase_order[order_info["orderRef"]] = order_info
            self.to_chase_order_lock.release()
        to_cancel_order = STesOptCancelOrder(
            orderRef=order_info["orderRef"].encode()
        )
        err = STesError()
        seq_id = self.gen_seq_num()
        self.opt_wrapper.opt_api_cancel(order_info["api_t"], byref(to_cancel_order), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when cancel order, err msg: " + str(get_data(err)))

    def query_order(self, api_t: int) -> None:
        err = STesError()
        seq_id = self.gen_seq_num()
        query = STesOptQueryOrder()
        self.opt_wrapper.opt_api_query_orders(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query order, err msg: " + str(get_data(err)))

    def save_order(self, order: STesOptOrder, opt_api_t: int) -> None:
        order_data = get_data(order)
        order_data["api_t"] = opt_api_t
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
        query = STesOptQueryTrade()
        seq_id = self.gen_seq_num()
        self.opt_wrapper.opt_api_query_trades(api_t, byref(query), seq_id, byref(err))
        if err.errid != 0:
            logging.error("error occurred when query trade, err msg: " + str(get_data(err)))

    def save_trade(self, trade: STesOptTrade) -> None:
        trade_data = get_data(trade)
        self.trade_data_lock.acquire()
        self.trade_data.append(trade_data)
        self.trade_data_lock.release()

    def query_position(self, api_t: int) -> None:
        err = STesError()
        query = STesOptQueryPosition()
        seq_id = self.gen_seq_num()
        self.opt_wrapper.opt_api_query_positions(api_t, byref(query), seq_id, byref(err))

    def save_position(self, position: STesOptPosition) -> None:
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
        underlying = position_data["underlyingCode"][:6]
        if position_data["account"] not in self.position_for_delta:
            self.position_for_delta[position_data["account"]] = {}
        if underlying not in self.position_for_delta[position_data["account"]]:
            self.position_for_delta[position_data["account"]][underlying] = {}
        if position_data["symbol"] not in self.position_for_delta[position_data["account"]][underlying]:
            self.position_for_delta[position_data["account"]][underlying][position_data["symbol"]] = {}
        self.position_for_delta[position_data["account"]][underlying][position_data["symbol"]][position_data["posType"]] = position_data


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
    def on_connected(opt_api_t: int) -> None:
        api_pool = get_api_pool()
        api_pool.set_status_by_api(opt_api_t, "connected")

        account_id = api_pool.get_api_info_by_api_t(opt_api_t).get_account_id()
        logging.info("connect account {0} successfully".format(account_id))

        option_trade = get_option_trade()
        seq_id = option_trade.gen_seq_num()
        err = STesError()
        option_trade.opt_wrapper.opt_api_login(opt_api_t, seq_id, byref(err))

    @staticmethod
    def on_disconnected(opt_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rsp_login(opt_api_t: int, rsp_login: POINTER(STesRspLogin), error: POINTER(STesError), req_id: int,
                     is_last: bool) -> None:
        err = error.contents
        # if is_last:
        if err.errid != 0:
            logging.warning("error occurred on login, err msg: " + str(get_data(err)))
            return
        rsp_login_data = rsp_login.contents
        client_id = rsp_login_data.clientID
        api_pool = get_api_pool()
        api_info = api_pool.get_api_info_by_api_t(opt_api_t)
        api_info.update_client_id(client_id)
        api_info.update_status("login")

        account_id = api_info.get_account_id()
        logging.info("login account {0} successfully".format(account_id))

    @staticmethod
    def on_rsp_logout(opt_api_t: int, rsp_logout: POINTER(STesRspLogout), error: POINTER(STesError), req_id: int,
                      is_last: bool) -> None:
        pass

    @staticmethod
    def on_ready(opt_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        err = error.contents
        if err.errid != 0:
            logging.warning("error occurred on ready, err msg: " + str(get_data(err)))
            return
        option_trade = get_option_trade()
        option_trade.query_order(opt_api_t)
        option_trade.query_trade(opt_api_t)
        option_trade.query_position(opt_api_t)

        api_pool = get_api_pool()
        api_pool.set_status_by_api(opt_api_t, "ready")

        account_id = api_pool.get_api_info_by_api_t(opt_api_t).get_account_id()
        logging.info("account {0} is ready".format(account_id))

    @staticmethod
    def on_req_error(opt_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_error(opt_api_t: int, error: POINTER(STesError), req_id: int) -> None:
        pass

    @staticmethod
    def on_rsp_entrust_order(opt_api_t: int, entrust_order: POINTER(STesOptEntrustOrder), error: POINTER(STesError),
                             req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_cancel_order(opt_api_t: int, cancel_order: POINTER(STesOptCancelOrder), error: POINTER(STesError),
                            req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_capital(opt_api_t: int, capital: POINTER(STesOptCapital), error: POINTER(STesError), req_id: int,
                             is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_contract(opt_api_t: int, contract: POINTER(STesOptContract), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_order(opt_api_t: int, opt_order: POINTER(STesOptOrder), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(opt_api_t).get_account_id()
            logging.warning("error on rsp query order for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_option_trade().save_order(opt_order.contents, opt_api_t)

    @staticmethod
    def on_rsp_query_trade(opt_api_t: int, opt_trade: POINTER(STesOptTrade), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(opt_api_t).get_account_id()
            logging.warning("error on rsp query trade for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_option_trade().save_trade(opt_trade.contents)

    @staticmethod
    def on_rsp_query_position(opt_api_t: int, opt_position: POINTER(STesOptPosition), error: POINTER(STesError),
                              req_id: int, is_last: bool) -> None:
        err = error.contents
        if err.errid != 0:
            account_id = get_api_pool().get_api_info_by_api_t(opt_api_t).get_account_id()
            logging.warning(
                "error on rsp query position for account {1}, error msg: {0}".format(get_data(err), account_id))
            return
        get_option_trade().save_position(opt_position.contents)

    @staticmethod
    def on_rsp_query_quote(opt_api_t: int, opt_quote: POINTER(STesOptQuoteData), error: POINTER(STesError), req_id: int,
                           is_last: bool) -> None:
        pass

    @staticmethod
    def on_rtn_error(opt_api_t: int, error: POINTER(STesError)) -> None:
        pass

    @staticmethod
    def on_rtn_order(opt_api_t: int, opt_order: POINTER(STesOptOrder)) -> None:
        get_option_trade().save_order(opt_order.contents, opt_api_t)

    @staticmethod
    def on_rtn_trade(opt_api_t: int, opt_trade: POINTER(STesOptTrade)) -> None:
        get_option_trade().save_trade(opt_trade.contents)

    @staticmethod
    def on_position_change(opt_api_t: int, opt_position: POINTER(STesOptPosition)) -> None:
        get_option_trade().save_position(opt_position.contents)

    @staticmethod
    def on_contract_status_change(opt_api_t: int,
                                  opt_contract_status_change: POINTER(STesOptContractStatusChange)) -> None:
        pass

    @staticmethod
    def on_rsp_covered_lock(opt_api_t: int, opt_lock_request: POINTER(STesOptLockRequest), error: POINTER(STesError),
                            req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_lock_order(opt_api_t: int, opt_lock_order: POINTER(STesOptLockOrder), error: POINTER(STesError),
                                req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_lock_position(opt_api_t: int, opt_lock_position: POINTER(STesOptLockPosition),
                                   error: POINTER(STesError), req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rtn_lock(opt_api_t: int, opt_lock_order: POINTER(STesOptLockOrder)) -> None:
        pass

    @staticmethod
    def on_lock_position_change(opt_api_t: int, opt_lock_position: POINTER(STesOptLockPosition)) -> None:
        pass

    @staticmethod
    def on_rsp_entrust_exec_order(opt_api_t: int, opt_entrust_exec_order: POINTER(STesOptEntrustExecOrder),
                                  error: POINTER(STesError), req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_cancel_exec_order(opt_api_t: int, opt_cancel_exec_order: POINTER(STesOptCancelExecOrder),
                                 error: POINTER(STesError), req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rsp_query_exec_order(opt_api_t: int, opt_exec_order: POINTER(STesOptExecOrder), error: POINTER(STesError),
                                req_id: int, is_last: bool) -> None:
        pass

    @staticmethod
    def on_rtn_exec_order(opt_api_t: int, opt_exec_order: POINTER(STesOptExecOrder)) -> None:
        pass


_option_trade = None


def get_option_trade() -> OptionTrade:
    global _option_trade
    if not _option_trade:
        app_config = get_app_config()
        _option_trade = OptionTrade(app_config.opt_wrapper_path)
    return _option_trade
