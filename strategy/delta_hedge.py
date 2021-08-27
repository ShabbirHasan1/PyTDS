import logging

from trade_api import future_trade
from trade_api.option_trade import get_option_trade
from trade_api.future_trade import get_future_trade
from trade_api.stock_trade import get_stock_trade
from config.config import get_app_config
from data.account_data import get_account
from data.wrapper_data import get_api_pool
from data.quote_data import get_contract, get_wing_model_vol_stream_data, get_opt_quote_data, get_ftr_quote_data, \
    get_stk_quote_data
from dolphin_db.query_dolphin import get_ddb_query
from decorator import decorator
import time
import datetime
import threading
from typing import List, Set
from decimal import Decimal


@decorator
def timer(func, *args, **kwargs):
    t = datetime.datetime.now()
    res = func(*args, **kwargs)
    print("%s time cost:" % func.__name__, datetime.datetime.now() - t)
    return res


_underlying_level = {
    "510050": 5,
    "510300": 5,
    "159919": 5,
    "000300": 1
}


class DeltaHedge(object):
    def __init__(self) -> None:
        self.lock = threading.Lock()
        contract_ob = get_contract()
        self.opt_contracts = contract_ob.opt_contract
        self.ftr_contracts = contract_ob.ftr_contract
        self.stk_contracts = contract_ob.stk_contract
        self.opt_underlying_total_count = contract_ob.opt_underlying_total_count
        self.opt_synthetic_group = contract_ob.opt_group_for_synthetic
        self.wing_model_vol_stream_data = get_wing_model_vol_stream_data()
        self.delta_multiplier = 10000
        self.delta_target = 0 * self.delta_multiplier
        self.delta_threshold = 100 * self.delta_multiplier
        self.delta_warning = 200 * self.delta_multiplier
        self.target_underlying_list: List[str] = []
        # 1 buy call sell put, 2 buy put sell call
        self.buy_synthetic = {1: set(), 2: set()}
        self.selected_synthetic: Set[tuple] = set()
        self.buy_call_synthetic_quote = {}
        self.buy_put_synthetic_quote = {}
        self.trade_account_list: List[str] = []
        self.option_trade_account = ""
        self.index_option_trade_account = ""
        self.future_trade_account = ""
        self.stock_trade_account = ""
        self.opt_quote_data_ob = get_opt_quote_data()
        self.ftr_quote_data_ob = get_ftr_quote_data()
        self.stk_quote_data_ob = get_stk_quote_data()
        self.tick_num = 0

        self.api_pool = get_api_pool()
        account_ob = get_account()
        self.accounts = account_ob.get_account()
        self.app_config = get_app_config()
        self.option_trade_ob = get_option_trade()
        self.future_trade_ob = get_future_trade()
        self.stock_trade_ob = get_stock_trade()
        self.trade_is_ready = False
        self.quote_is_ready = False

    def set_target_underlying_list(self, underlying_list: list) -> bool:
        if not isinstance(underlying_list, list):
            logging.error("target underlying must be a list")
            return False
        for underlying in underlying_list:
            if underlying not in self.opt_underlying_total_count:
                logging.error("underlying %s is illegal" % underlying)
                self.target_underlying_list.clear()
                return False
            if underlying in self.target_underlying_list:
                logging.warning("duplicate target underlying %s, ignored" % underlying)
                continue
            self.target_underlying_list.append(underlying)
        return True

    def set_tick_num(self, tick_num: int) -> bool:
        if not isinstance(tick_num, int):
            logging.error("tick num must be int")
            return False
        self.tick_num = tick_num
        return True

    # (underlying, expire_date, strike_price, buy_type)
    def set_buy_synthetic(self, synthetic_list: List[tuple]) -> bool:
        if not isinstance(synthetic_list, list):
            logging.error("trade synthetic must be a list")
            return False
        for e in synthetic_list:
            if e[0] not in self.opt_synthetic_group:
                logging.error("cannot find underlying %s" % e[0])
                self.buy_synthetic.clear()
                return False
            if e[1] not in self.opt_synthetic_group[e[0]]:
                logging.error("cannot find expire date %s for underlying %s" % (e[1], e[0]))
                self.buy_synthetic.clear()
                return False
            if e[2] not in self.opt_synthetic_group[e[0]][e[1]]:
                logging.error("cannot find strike price %s for underlying %s, expire date %s" % (e[2], e[0], e[1]))
                self.buy_synthetic.clear()
                return False
            synthetic_key = (e[0], e[1], e[2])
            self.selected_synthetic.add(synthetic_key)
            if e[3] == 1 or e[3] == "call":
                self.buy_synthetic[1].add(synthetic_key)
            elif e[3] == 2 or e[3] == "put":
                self.buy_synthetic[2].add(synthetic_key)
            else:
                self.buy_synthetic.clear()
                logging.error("type error for current synthetic future %s" % e)
                return False
        return True

    def set_trade_account(self, account_list: list) -> bool:
        if not isinstance(account_list, list):
            logging.error("trade account must be a list")
            return False
        for account in account_list:
            if account not in self.accounts:
                logging.error("account %s is illegal" % account)
                self.trade_account_list.clear()
                return False
            self.trade_account_list.append(account)
        return True

    def check_trade_is_ready(self) -> bool:
        trade_type_set = set()
        if self.trade_is_ready:
            return True

        if not self.tick_num:
            logging.warning("tick num is not set, default tick num is 0")
        else:
            pass

        if not self.buy_synthetic:
            logging.error("buy synthetic not set yet")
            return False
        else:
            pass

        if not self.target_underlying_list:
            logging.error("target underlying is not set yet")
            return False
        else:
            pass

        if not self.trade_account_list:
            logging.error("trade account is not set yet")
            return False
        else:
            for account in self.trade_account_list:
                api_info = self.api_pool.get_api_info_by_account(account)
                if not api_info:
                    logging.error("account %s is not ready" % account)
                    return False
                else:
                    if api_info.get_status() != "ready":
                        logging.error("account %s is not ready" % account)
                        return False
                    else:
                        pass
                if self.accounts[account]["trade_type"] in trade_type_set:
                    logging.error("multiple %s account exist" % self.accounts[account]["trade_type"])
                    return False
                trade_type_set.add(self.accounts[account]["trade_type"])
                if self.accounts[account]["trade_type"] == "OptionTrade":
                    self.option_trade_account = account
                elif self.accounts[account]["trade_type"] == "IndexOptionTrade":
                    self.index_option_trade_account = account
                elif self.accounts[account]["trade_type"] == "FutureTrade":
                    self.future_trade_account = account
                elif self.accounts[account]["trade_type"] == "StockTrade":
                    self.stock_trade_account = account
                else:
                    pass

        for underlying in self.target_underlying_list:
            if underlying == "510050" or underlying == "510300" or underlying == "159919":
                if "OptionTrade" not in trade_type_set:
                    logging.error("option trade account is not ready")
                    return False
            if underlying == "000300":
                if "IndexOptionTrade" not in trade_type_set:
                    logging.error("index option trade account is not ready")
                    return False

        self.trade_is_ready = True
        return True

    def check_quote_is_ready(self) -> bool:
        if not self.trade_is_ready:
            logging.error("trade is not ready")
            return False
        if self.quote_is_ready:
            return True
        wing = get_wing_model_vol_stream_data()
        wing_data = wing.get_quote()
        for underlying in self.target_underlying_list:
            if len(wing_data[underlying]) != self.opt_underlying_total_count[underlying]:
                logging.error("wing data of underlying %s is not filled" % underlying)
                return False
        self.quote_is_ready = True
        return True

    @timer
    def get_trade_synthetic_future_quote(self) -> tuple:
        # cur_quote = self.opt_quote_data_ob.get_quote()
        opt_quote_index = self.opt_quote_data_ob.get_opt_quote_index()
        # e[0] underlying e[1] expire date e[2] strike price
        # synthetic_quote = {}
        buy_call_synthetic_quote = []
        buy_put_synthetic_quote = []

        for e in self.selected_synthetic:
            synthetic_key = (e[0], e[1], e[2])
            call_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][1]
            put_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][2]
            # call_quote = cur_quote[call_contract["symbol"]]
            # put_quote = cur_quote[put_contract["symbol"]]
            call_quote = self.opt_quote_data_ob.get_quote_with_symbol(call_contract["symbol"])
            put_quote = self.opt_quote_data_ob.get_quote_with_symbol(put_contract["symbol"])
            level = _underlying_level[e[0]]
            buy_call_volume = 0
            buy_put_volume = 0
            sell_call_volume = 0
            sell_put_volume = 0
            for cur_level in range(1, level + 1):
                bid_volume_key = "bidVolume%d" % cur_level
                ask_volume_key = "askVolume%d" % cur_level
                bid_price_key = "bidPrice%d" % cur_level
                ask_price_key = "askPrice%d" % cur_level
                level_key = "level_%d" % cur_level

                buy_call_volume += call_quote[opt_quote_index[bid_volume_key]]
                buy_put_volume += put_quote[opt_quote_index[ask_volume_key]]
                sell_call_volume += call_quote[opt_quote_index[ask_volume_key]]
                sell_put_volume += put_quote[opt_quote_index[bid_volume_key]]

                synthetic_buy_volume = min(buy_call_volume, buy_put_volume)
                synthetic_sell_volume = min(sell_call_volume, sell_put_volume)
                synthetic_buy_price = float(
                    Decimal(str(e[2])) + Decimal(str(call_quote[opt_quote_index[bid_price_key]])) - Decimal(
                        str(put_quote[opt_quote_index[ask_price_key]])))
                synthetic_sell_price = float(
                    Decimal(str(e[2])) + Decimal(str(call_quote[opt_quote_index[ask_price_key]])) - Decimal(
                        str(put_quote[opt_quote_index[bid_price_key]])))

                cur_synthetic_quote = [synthetic_buy_volume, synthetic_buy_price, synthetic_sell_volume,
                                       synthetic_sell_price]

                # if synthetic_key not in synthetic_quote:
                #     synthetic_quote[synthetic_key] = {}
                # synthetic_quote[synthetic_key][level_key] = cur_synthetic_quote

                if synthetic_key in self.buy_synthetic[1]:
                    buy_call_synthetic_quote.append([
                        level_key,
                        synthetic_buy_volume,
                        synthetic_buy_price,
                        synthetic_sell_volume,
                        synthetic_sell_price,
                        synthetic_key,
                    ])

                if synthetic_key in self.buy_synthetic[2]:
                    buy_put_synthetic_quote.append([
                        level_key,
                        synthetic_buy_volume,
                        synthetic_buy_price,
                        synthetic_sell_volume,
                        synthetic_sell_price,
                        synthetic_key,
                    ])

        buy_call_synthetic_quote = sorted(buy_call_synthetic_quote, key=lambda e: e[2])
        buy_put_synthetic_quote = sorted(buy_put_synthetic_quote, key=lambda e: e[4])

        return buy_call_synthetic_quote, buy_put_synthetic_quote

    @timer()
    def calc_total_pos_delta(self) -> float:
        total_delta = 0
        opt_pos_data = self.option_trade_ob.get_position_for_delta()
        ftr_pos_data = self.future_trade_ob.get_position_for_delta()
        stk_pos_data = self.stock_trade_ob.get_position_for_delta()
        for account in opt_pos_data:
            if account not in self.trade_account_list:
                continue
            for underlying in opt_pos_data[account]:
                if underlying not in self.target_underlying_list:
                    continue
                for symbol in opt_pos_data[account][underlying]:
                    total_pos = 0
                    for pos_type in opt_pos_data[account][underlying][symbol]:
                        if pos_type == 1:
                            total_pos += opt_pos_data[account][underlying][symbol][pos_type]["totalPos"]
                        else:
                            total_pos -= opt_pos_data[account][underlying][symbol][pos_type]["totalPos"]
                    if total_pos == 0:
                        continue
                    total_delta += total_pos * self.wing_model_vol_stream_data.get_delta_by_symbol(
                        symbol) * self.wing_model_vol_stream_data.get_future_price_by_symbol(symbol) * \
                                   self.opt_contracts[symbol]["multiple"]

        for account in ftr_pos_data:
            if account not in self.trade_account_list:
                continue
            for underlying in ftr_pos_data[account]:
                if underlying not in self.target_underlying_list:
                    continue
                for symbol in ftr_pos_data[account][underlying]:
                    total_pos = 0
                    for pos_type in ftr_pos_data[account][underlying][symbol]:
                        if pos_type == 1:
                            total_pos += ftr_pos_data[underlying][symbol][pos_type]["totalPos"]
                        else:
                            total_pos -= ftr_pos_data[underlying][symbol][pos_type]["totalPos"]
                    if total_pos == 0:
                        continue
                    total_delta += total_pos * self.ftr_quote_data_ob.get_quote_with_symbol(symbol) * \
                                   self.ftr_contracts[symbol]["multiple"]

        for account in stk_pos_data:
            if account not in self.trade_account_list:
                continue
            for symbol in stk_pos_data[account]:
                if symbol not in self.target_underlying_list:
                    continue
                if stk_pos_data[account][symbol]["totalPos"] == 0:
                    continue
                total_delta += stk_pos_data[account][symbol]["totalPos"] * self.stk_quote_data_ob.get_quote_with_symbol(
                    symbol)

        return total_delta

    @timer
    def start_delta_hedge(self):
        total_delta = self.calc_total_pos_delta()
        delta_offset = total_delta - self.delta_target
        if delta_offset >= self.delta_warning:
            logging.warning("delta reach warning, stop loop")
            return
        if delta_offset >= self.delta_threshold:
            logging.info("reach delta threshold, start hedge")
            self.do_delta_hedge(total_delta)
        else:
            logging.info("not reach delta threshold, do nothing")

    def do_delta_hedge(self, delta_offset: float):
        buy_call_synthetic_quote, buy_put_synthetic_quote = self.get_trade_synthetic_future_quote()
        if delta_offset > 0:
            pass
        else:
            pass


_delta_hedge = None


def get_delta_hedge() -> DeltaHedge:
    global _delta_hedge
    if not _delta_hedge:
        _delta_hedge = DeltaHedge()
    return _delta_hedge


if __name__ == '__main__':
    from dolphin_db.sub_dolphin import get_ddb_sub

    sub_ddb_ob = get_ddb_sub()
    sub_ddb_ob.subscribe_wing_model()
    sub_ddb_ob.subscribe_option_quote()
    opt_quote_ob = get_opt_quote_data()
    wing_data_ob = get_wing_model_vol_stream_data()
    query_ddb_ob = get_ddb_query()
    recent_wing = query_ddb_ob.query_wing_data()
    recent_option = query_ddb_ob.query_option_quote()

    for row in recent_option:
        opt_quote_ob.update_quote(row)
    for row in recent_wing:
        wing_data_ob.update_quote(row)
    accounts = get_account().accounts
    option_trade_ob = get_option_trade()
    future_trade_ob = get_future_trade()
    stock_trade_ob = get_stock_trade()
    delta = DeltaHedge()
    delta.set_tick_num(1)
    delta.set_buy_synthetic([
        ("510050", 202109, 4.4, "put"),
        ("510050", 202109, 4.5, "call"),
        ("510050", 202109, 4.6, "put"),
        ("510050", 202109, 4.7, "call"),
        ("510050", 202109, 4.8, "put"),
        ("510050", 202109, 4.9, "call"),
        ("510050", 202109, 5.0, "put"),
        ("510050", 202109, 5.25, "call"),
    ])
    # delta.set_trade_account(["222"])
    # delta.set_trade_account(["177"])
    # delta.set_trade_account(["178"])
    delta.set_trade_account(["178", "177"])
    # delta.set_target_underlying_list(["510050"])
    # delta.set_target_underlying_list(["510300"])
    # delta.set_target_underlying_list(["159919"])
    delta.set_target_underlying_list(["000300", "510300", "159919"])
    # delta.set_target_underlying_list(["510300", "159919", "000300"])

    option_trade_ob.login_account(accounts["177"])
    option_trade_ob.login_account(accounts["178"])
    # option_trade_ob.login_account(accounts["222"])

    future_trade_ob.login_account(accounts["176"])
    # stock_trade_ob.login_account(accounts[""])

    time.sleep(15)
    is_ready = delta.check_trade_is_ready()
    if not is_ready:
        print("account not ready")
    else:
        print("account is ready")

        buy_call_quote, buy_put_quote = delta.get_trade_synthetic_future_quote()

        total_delta = delta.calc_total_pos_delta()
        print(total_delta, round(total_delta / 10000, 1))
