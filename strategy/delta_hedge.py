import numpy as np
import numba as nb
import pandas as pd
import logging
from trade_api.option_trade import get_option_trade
from config.config import get_app_config
from data.account_data import get_account
from data.wrapper_data import get_api_pool
from data.quote_data import get_contract, get_wing_model_vol_stream_data, get_opt_quote_data
import threading
from typing import List, Set
from decimal import Decimal

# _underlying_list = [
#     "510050",
#     "510300",
#     "159919",
#     "000300"
# ]

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
        self.target_underlying_list: List[str] = []
        self.buy_synthetic = {1: [], 2: []}
        self.selected_synthetic: Set[tuple] = set()
        self.buy_call_synthetic_quote = {}
        self.buy_put_synthetic_quote = {}
        self.trade_account_list: List[str] = []
        self.opt_quote_data_ob = get_opt_quote_data()

        self.api_pool = get_api_pool()
        account_ob = get_account()
        self.accounts = account_ob.get_account()
        self.app_config = get_app_config()
        self.option_trade = get_option_trade()
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

    # (underlying, expire_date, strike_price, type)
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
            # if e[3] not in self.opt_synthetic_group[e[0]][e[1]][e[2]]:
            #     logging.error("cannot find type % for underlying %s, expire_date %s, strike price %s" % (e[3], e[0], e[1], e[2]))
            #     self.buy_synthetic_list.clear()
            #     return False
            self.selected_synthetic.add((e[0], e[1], e[2]))
            if e[3] == 1 or e[3] == "call":
                self.buy_synthetic[1].append(e)
            elif e[3] == 2 or e[3] == "put":
                self.buy_synthetic[2].append(e)
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

    def get_trade_synthetic_future_quote(self):
        cur_quote = self.opt_quote_data_ob.get_quote()
        # e[0] underlying e[1] expire date e[2] strike price
        res_quote = {}
        for e in self.selected_synthetic:
            key = (e[0], e[1], e[2])
            call_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][1]
            put_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][2]
            call_quote = cur_quote[call_contract["symbol"]]
            put_quote = cur_quote[put_contract["symbol"]]

            if e[0] == "000300":
                quote = {"level1": {}}
                buy_call_volume = call_quote["bidVolume1"]
                buy_put_volume = put_quote["askVolume1"]
                sell_call_volume = call_quote["askVolume1"]
                sell_put_volume = put_quote["bidVolume1"]

                buy_volume = min(buy_call_volume, buy_put_volume)
                sell_volume = min(sell_call_volume, sell_put_volume)

                buy_price = float(Decimal(str(e[2])) + Decimal(str(call_quote["bidPrice1"])) - Decimal(str(put_quote["askPrice1"])))
                sell_price = float(Decimal(str(e[2])) + Decimal(str(call_quote["askPrice1"])) - Decimal(str(put_quote["bidPrice1"])))

                quote["level1"]["buy_volume"] = buy_volume
                quote["level1"]["sell_volume"] = sell_volume
                quote["level1"]["buy_price"] = buy_price
                quote["level1"]["sell_price"] = sell_price

                res_quote[key] = {
                    "level1": {
                        "buy_volume": buy_volume,
                        "sell_volume": sell_volume,
                        "buy_price": buy_price,
                        "sell_price": sell_price
                    }
                }
            else:
                pass









    def gen_buy_put_synthetic_future(self):
        pass









_delta_hedge = None

def get_delta_hedge() -> DeltaHedge:
    global _delta_hedge
    if not _delta_hedge:
        _delta_hedge = DeltaHedge()
    return _delta_hedge

if __name__ == '__main__':
    get_delta_hedge()