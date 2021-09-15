import logging
from decimal import Decimal
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
import math

_final_status = {"F", "T", "C", "B", "R", "D"}
_underlying_level = {
    "510050": 5,
    "510300": 5,
    "159919": 5,
    "000300": 1
}
_hedge_flag = 1

@decorator
def timer(func, *args, **kwargs):
    t = datetime.datetime.now()
    res = func(*args, **kwargs)
    print("%s time cost:" % func.__name__, datetime.datetime.now() - t)
    return res


class DeltaHedge(object):
    def __init__(self) -> None:
        self.lock = threading.Lock()

        account_ob = get_account()
        self.accounts = account_ob.get_account()

        contract_ob = get_contract()
        self.opt_contracts = contract_ob.opt_contract
        self.ftr_contracts = contract_ob.ftr_contract
        self.stk_contracts = contract_ob.stk_contract
        self.opt_synthetic_group = contract_ob.opt_group_for_synthetic

        self.opt_quote_ob = get_opt_quote_data()
        self.ftr_quote_ob = get_ftr_quote_data()
        self.stk_quote_ob = get_stk_quote_data()
        self.opt_wing_ob = get_wing_model_vol_stream_data()

        self.opt_trade_ob = get_option_trade()
        self.ftr_trade_ob = get_future_trade()
        self.stk_trade_ob = get_stock_trade()

        self.option_account_id = ""
        self.option_account_api_t = 0
        self.option_account_client_id = 0
        self.index_option_account_id = ""
        self.index_option_account_api_t = 0
        self.index_option_account_client_id = 0
        self.future_account_id = ""
        self.future_account_api_t = 0
        self.future_account_client_id = 0
        self.stock_account_id = ""
        self.stock_account_api_t = 0
        self.stock_account_client_id = 0
        self.trade_account_set = set()
        self.trade_account_set.add(self.option_account_id)
        self.trade_account_set.add(self.index_option_account_id)
        self.trade_account_set.add(self.future_account_id)
        self.trade_account_set.add(self.stock_account_id)

        self.underlying_set = set()

        self.chase_limit_num = 5
        self.tick_num = 0

        self.cur_total_pos_delta = 0
        self.delta_multiplier = 10000
        self.delta_target = 0 * self.delta_multiplier
        self.delta_threshold = 100 * self.delta_multiplier
        self.delta_limit = 50000 * self.delta_multiplier

        # (underlying, expire date, strike price)
        self.to_buy_synthetic_set = set()
        self.to_sell_synthetic_set = set()

        # synthetic with quote
        self.to_buy_synthetic_list = []
        self.to_sell_synthetic_list = []

        self.to_order_symbol_pos = dict()

    def calc_total_pos_delta(self) -> None:
        total_delta = 0
        opt_pos_data = self.opt_trade_ob.get_position_for_delta()
        ftr_pos_data = self.ftr_trade_ob.get_position_for_delta()
        stk_pos_data = self.stk_trade_ob.get_position_for_delta()
        for account in opt_pos_data:
            if account not in self.trade_account_set:
                continue
            for underlying in opt_pos_data[account]:
                if underlying not in self.underlying_set:
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
                    total_delta += total_pos * self.opt_wing_ob.get_delta_by_symbol(
                        symbol) * self.opt_wing_ob.get_future_price_by_symbol(symbol) * \
                                   self.opt_contracts[symbol]["multiple"]

        product_list = []
        for account in ftr_pos_data:
            if account not in self.trade_account_set:
                continue
            if "510050" in self.underlying_set:
                product_list.append("IH")
            if "510300" in self.underlying_set or "000300" in self.underlying_set or "159919" in self.underlying_set:
                product_list.append("IF")
            for product in ftr_pos_data[account]:
                if product not in product_list:
                    continue
                for symbol in ftr_pos_data[account][product]:
                    total_pos = 0
                    for pos_type in ftr_pos_data[account][product][symbol]:
                        if pos_type == 1:
                            total_pos += ftr_pos_data[product][symbol][pos_type]["totalPos"]
                        else:
                            total_pos -= ftr_pos_data[product][symbol][pos_type]["totalPos"]
                    if total_pos == 0:
                        continue
                    total_delta += total_pos * self.ftr_quote_ob.get_last_price_by_symbol(symbol) * \
                                   self.ftr_contracts[symbol]["multiple"]

        for account in stk_pos_data:
            if account not in self.trade_account_set:
                continue
            for symbol in stk_pos_data[account]:
                if symbol not in self.underlying_set:
                    continue
                if stk_pos_data[account][symbol]["totalPos"] == 0:
                    continue
                total_delta += stk_pos_data[account][symbol][
                                   "totalPos"] * self.stk_quote_ob.get_last_price_by_symbol(
                    symbol)

        self.cur_total_pos_delta = total_delta
        print("total pos delta:", total_delta, total_delta // self.delta_multiplier)

    def calc_synthetic_future_quote(self) -> None:
        opt_quote_index = self.opt_quote_ob.get_opt_quote_index()
        to_buy_synthetic_list = []
        to_sell_synthetic_list = []

        full_synthetic_set = self.to_buy_synthetic_set.union(self.to_sell_synthetic_set)

        for e in full_synthetic_set:
            call_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][1]
            put_contract = self.opt_synthetic_group[e[0]][e[1]][e[2]][2]

            call_quote = self.opt_quote_ob.get_quote_by_symbol(call_contract["symbol"])
            put_quote = self.opt_quote_ob.get_quote_by_symbol(put_contract["symbol"])

            # quote level + 1
            max_level = _underlying_level[e[0]] + 1

            for cur_level in range(1, max_level):
                bid_volume_key = "bidVolume%d" % cur_level
                ask_volume_key = "askVolume%d" % cur_level
                bid_price_key = "bidPrice%d" % cur_level
                ask_price_key = "askPrice%d" % cur_level

                buy_call_volume = call_quote[opt_quote_index[bid_volume_key]]
                buy_put_volume = put_quote[opt_quote_index[bid_volume_key]]
                sell_call_volume = call_quote[opt_quote_index[ask_volume_key]]
                sell_put_volume = put_quote[opt_quote_index[ask_volume_key]]

                synthetic_buy_volume = min(buy_call_volume, sell_put_volume)
                synthetic_sell_volume = min(sell_call_volume, buy_put_volume)

                call_bid_price = call_quote[opt_quote_index[bid_price_key]]
                call_ask_price = call_quote[opt_quote_index[ask_price_key]]
                put_bid_price = put_quote[opt_quote_index[bid_price_key]]
                put_ask_price = put_quote[opt_quote_index[ask_price_key]]

                synthetic_buy_price = e[2] + call_bid_price - put_ask_price
                synthetic_sell_price = e[2] + call_ask_price - put_bid_price

                if call_bid_price == 0:
                    continue
                if call_ask_price == 0:
                    continue
                if put_bid_price == 0:
                    continue
                if put_ask_price == 0:
                    continue

                if e in self.to_buy_synthetic_set:
                    # [synthetic volume, synthetic price, buy contract, buy price, sell contract, sell price]
                    to_buy_synthetic_list.append([
                        synthetic_buy_volume,
                        synthetic_buy_price,
                        call_contract,  # buy call contract
                        call_ask_price,  # buy with call ask price
                        put_contract,  # sell put contract
                        put_bid_price  # sell with put bid price
                    ])

                if e in self.to_sell_synthetic_set:
                    # [synthetic volume, synthetic price, buy contract, buy price, sell contract, sell price]
                    to_sell_synthetic_list.append([
                        synthetic_sell_volume,
                        synthetic_sell_price,
                        put_contract,  # buy put contract
                        put_ask_price,  # buy with put ask price
                        call_contract,  # sell call contract
                        call_bid_price  # sell with call bid price
                    ])

        self.to_buy_synthetic_list = sorted(to_buy_synthetic_list, key=lambda e: e[1])
        self.to_sell_synthetic_list = sorted(to_sell_synthetic_list, key=lambda e: e[1], reverse=True)

    def calc_synthetic_volume(self, delta_diff: float) -> int:
        best_syn_f = self.opt_wing_ob.get_near_best_future_price()
        volume = delta_diff / best_syn_f / 10000
        print("to order volume:", int(volume))
        return int(volume)

    def calc_orders(self, delta_diff: float) -> list:
        closeable_pos_dict = {}
        to_order_symbol_set = set()
        api_pool = get_api_pool()
        if self.option_account_id:
            option_api_info = api_pool.get_api_info_by_account(self.option_account_id)
            if not option_api_info:
                print("option account not connected")
                return []
            else:
                self.option_account_api_t = option_api_info.get_api_t()
                if not self.option_account_api_t:
                    print("option account not connected")
                    return []
                self.option_account_client_id = option_api_info.get_client_id()
                if not self.option_account_client_id:
                    print("option account not connected")
                    return []
        if self.index_option_account_id:
            index_option_api_info = api_pool.get_api_info_by_account(self.index_option_account_id)
            if not index_option_api_info:
                print("index option account not connected")
                return []
            else:
                self.index_option_account_api_t = index_option_api_info.get_api_t()
                if not self.index_option_account_api_t:
                    print("index option account not connected")
                    return []
                self.index_option_account_client_id = index_option_api_info.get_client_id()
                if not self.index_option_account_client_id:
                    print("index option account not connected")
                    return []
        if self.future_account_id:
            # todo
            pass
        if self.stock_account_id:
            # todo
            pass

        remain_volume = self.calc_synthetic_volume(delta_diff)
        if remain_volume > 0:
            synthetic_list = self.to_sell_synthetic_list
        elif remain_volume < 0:
            remain_volume = -remain_volume
            synthetic_list = self.to_buy_synthetic_list
        else:
            print("to order volume is zero")
            return []

        synthetic_list_length = len(synthetic_list)
        order_info_list = []
        synthetic_index = 0

        while remain_volume > 0 and synthetic_index < synthetic_list_length:
            best_synthetic = synthetic_list[synthetic_index]
            best_available_volume = best_synthetic[0]
            if best_available_volume >= remain_volume:
                volume = remain_volume
            else:
                volume = best_available_volume

            buy_contract = best_synthetic[2]
            cur_buy_symbol = buy_contract["symbol"]

            if cur_buy_symbol not in to_order_symbol_set:
                to_order_symbol_set.add(cur_buy_symbol)
                closeable_pos_dict[cur_buy_symbol] = self.calc_to_order_symbol_pos(buy_contract)

            buy_quote_price = best_synthetic[3]
            order_info_list += (self.gen_order_info(1, buy_contract, buy_quote_price, volume, closeable_pos_dict[cur_buy_symbol]))

            sell_contract = best_synthetic[4]
            cur_sell_symbol = sell_contract["symbol"]

            if cur_sell_symbol not in to_order_symbol_set:
                to_order_symbol_set.add(cur_sell_symbol)
                closeable_pos_dict[cur_sell_symbol] = self.calc_to_order_symbol_pos(sell_contract)

            sell_quote_price = best_synthetic[5]
            order_info_list += (self.gen_order_info(2, sell_contract, sell_quote_price, volume, closeable_pos_dict[cur_sell_symbol]))

            remain_volume -= volume
            synthetic_index += 1

        return order_info_list

    def calc_to_order_symbol_pos(self, contract: dict) -> dict:
        closeable_pos = {
            1: 0,
            2: 0
        }
        if contract["underlyingCode"] == "000300":
            account = self.index_option_account_id
        else:
            account = self.option_account_id

        position = self.opt_trade_ob.get_symbol_position(contract["symbol"], account)
        if position:
            for pos_type in position[_hedge_flag]:
                cur_pos = position[_hedge_flag][pos_type]
                closeable_pos[pos_type] = cur_pos["totalPos"] - cur_pos["frozenClosePos"]

        return closeable_pos

    def gen_order_info(self, direction: int, contract: dict, quote_price: float, volume: int, closeable_pos: dict) -> list:
        res = []
        underlying = contract["underlyingCode"]
        tick = contract["priceTick"]
        symbol = contract["symbol"]
        exchange = contract["exchange"]

        actual_direction = "B" if direction == 1 else "S"

        if underlying == "000300":
            account_id = self.index_option_account_client_id
            client_id = self.index_option_account_client_id
            api_t = self.index_option_account_api_t
        else:
            account_id = self.option_account_id
            client_id = self.option_account_client_id
            api_t = self.option_account_api_t

        price = quote_price + self.tick_num * tick if direction == 1 else quote_price - self.tick_num * tick

        if underlying != "000300":
            price = round(price, 4)
        else:
            price = round(price, 2) * 100
            if price % 2 != 0:
                price = (price - 1) / 100
            else:
                price = price / 100

        closeable_volume = closeable_pos[direction]

        if not closeable_volume:
            order_info = {
                "api_t": api_t,
                "account": account_id,
                "symbol": symbol,
                "exchange": exchange,
                "orderPriceType": "L",
                "direction": actual_direction,
                "offset": "O",
                "hedgeFlag": 1,
                "price": price,
                "volume": volume,
                "clientID": client_id,
                "trackCode": "delta_0"
            }
            res.append(order_info)
        else:
            if volume > closeable_volume:
                close_order_info = {
                    "api_t": api_t,
                    "account": account_id,
                    "symbol": symbol,
                    "exchange": exchange,
                    "orderPriceType": "L",
                    "direction": actual_direction,
                    "offset": "C",
                    "hedgeFlag": 1,
                    "price": price,
                    "volume": closeable_volume,
                    "clientID": client_id,
                    "trackCode": "delta_0"
                }
                res.append(close_order_info)
                open_order_info = {
                    "api_t": api_t,
                    "account": account_id,
                    "symbol": symbol,
                    "exchange": exchange,
                    "orderPriceType": "L",
                    "direction": actual_direction,
                    "offset": "O",
                    "hedgeFlag": 1,
                    "price": price,
                    "volume": volume - closeable_volume,
                    "clientID": client_id,
                    "trackCode": "delta_0"
                }
                res.append(open_order_info)
                closeable_pos[direction] = 0
            else:
                close_order_info = {
                    "api_t": api_t,
                    "account": account_id,
                    "symbol": symbol,
                    "exchange": exchange,
                    "orderPriceType": "L",
                    "direction": actual_direction,
                    "offset": "C",
                    "hedgeFlag": 1,
                    "price": price,
                    "volume": volume,
                    "clientID": client_id,
                    "trackCode": "delta_0"
                }
                res.append(close_order_info)
                closeable_pos[direction] -= volume

        return res

    def make_order(self, order_info_list: list) -> None:
        # todo: assign tick
        for order_info in order_info_list:
            print(order_info)
            self.opt_trade_ob.entrust_order(order_info)

    def test_order(self):
        account_id = self.option_account_id
        option_api_info = get_api_pool().get_api_info_by_account(self.option_account_id)
        api_t = option_api_info.get_api_t()
        client_id = option_api_info.get_client_id()
        order_info = {
            "api_t": api_t,
            "account": account_id,
            "symbol": "10003323",
            "exchange": "SH",
            "orderPriceType": "L",
            "direction": "S",
            "offset": "C",
            "hedgeFlag": 1,
            "price": 0.47,
            "volume": 50,
            "clientID": client_id,
            "trackCode": "delta_0"
        }
        self.opt_trade_ob.entrust_order(order_info)


    def cancel_all_pending_order(self) -> None:
        for order_info in self.opt_trade_ob.delta_pending_order.values():
            self.opt_trade_ob.cancel_order(order_info)

    def do_delta_hedge(self):
        self.calc_total_pos_delta()
        delta_diff = self.cur_total_pos_delta - self.delta_target
        if abs(delta_diff) > self.delta_threshold:
            self.calc_synthetic_future_quote()
            order_info_list = self.calc_orders(delta_diff)
            self.make_order(order_info_list)
            time.sleep(0.5)

    def start(self):
        while True:
            self.calc_total_pos_delta()
            delta_diff = self.cur_total_pos_delta - self.delta_target
            if abs(delta_diff) > self.delta_threshold:
                while abs(delta_diff) / 10000 > self.opt_wing_ob.get_near_best_future_price():
                    self.calc_synthetic_future_quote()
                    order_info_list = self.calc_orders(delta_diff)
                    self.make_order(order_info_list)
                    time.sleep(0.5)
                    delta_diff = self.cur_total_pos_delta - self.delta_target
            time.sleep(0.5)




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


    delta = DeltaHedge()
    get_option_trade().login_account(delta.accounts["237"])
    time.sleep(10)

    delta.trade_account_set.add("237")
    delta.option_account_id = "237"

    delta.underlying_set = {"510300"}

    delta.to_buy_synthetic_set.add(("510300", 202109, 4.4))
    delta.to_buy_synthetic_set.add(("510300", 202109, 4.5))
    delta.to_buy_synthetic_set.add(("510300", 202109, 4.6))
    delta.to_buy_synthetic_set.add(("510300", 202109, 4.7))

    delta.to_sell_synthetic_set.add(("510300", 202109, 4.4))
    delta.to_sell_synthetic_set.add(("510300", 202109, 4.5))
    delta.to_sell_synthetic_set.add(("510300", 202109, 4.6))
    delta.to_sell_synthetic_set.add(("510300", 202109, 4.7))

    # delta.calc_total_pos_delta()

    # delta.start()

    #
    #
    # delta.do_delta_hedge()
    # time.sleep(5)
    # #
    delta.calc_total_pos_delta()
    #
    delta.test_order()
    time.sleep(3)

