import logging

import delta as delta

from data.trade_data import OptPositionData
from dolphin_db.query_dolphin import get_ddb_query
import threading
import copy
import time

_wing_index = {
    "user": 0,
    "underlier": 1,
    "symbol": 2,
    "future_price": 3,
    "bid1_price": 4,
    "ask1_price": 5,
    "vol": 6,
    "delta": 7,
    "cash_delta": 8,
    "gamma": 9,
    "pgamma": 10,
    "vega": 11,
    "theta": 12,
    "rho": 13,
    "vanna": 14,
    "charm": 15,
    "zomma": 16,
    "color": 17,
    "volga": 18,
    "speed": 19,
    "strike_price": 20,
    "theo_price": 21,
    "OptionsType": 22,
    "ExpireDate": 23,
    "update_time": 24,
}

# _wing_index = {
#     "user": 0,
#     "underlier": 1,
#     "symbol": 2,
#     "future_price": 3,
#     "bid1_price": 4,
#     "ask1_price": 5,
#     "vol": 6,
#     "delta": 7,
#     "cash_delta": 8,
#     "gamma": 9,
#     "pgamma": 10,
#     "vega": 11,
#     "theta": 12,
#     "rho": 13,
#     "vanna": 14,
#     "charm": 15,
#     "strike_price": 16,
#     "theo_price": 17,
#     "OptionsType": 18,
#     "ExpireDate": 19,
#     "update_time": 20,
# }

_opt_quote_index = {
    "symbol": 0,
    "market": 1,
    "tradingDay": 2,
    "date": 3,
    "time": 4,
    "preClose": 5,
    "open": 6,
    "high": 7,
    "low": 8,
    "close": 9,
    "last": 10,
    "curVol": 11,
    "volume": 12,
    "curTurnover": 13,
    "turnover": 14,
    "oi": 15,
    "settle": 16,
    "preOI": 17,
    "prSettle": 18,
    "auctionPrice": 19,
    "auctionVol": 20,
    "askLevel": 21,
    "bidLevel": 22,
    "askPrice1": 23,
    "askPrice2": 24,
    "askPrice3": 25,
    "askPrice4": 26,
    "askPrice5": 27,
    "bidPrice1": 28,
    "bidPrice2": 29,
    "bidPrice3": 30,
    "bidPrice4": 31,
    "bidPrice5": 32,
    "askVolume1": 33,
    "askVolume2": 34,
    "askVolume3": 35,
    "askVolume4": 36,
    "askVolume5": 37,
    "bidVolume1": 38,
    "bidVolume2": 39,
    "bidVolume3": 40,
    "bidVolume4": 41,
    "bidVolume5": 42,
    "status": 43,
    "unixTime": 44,
    "upperLimit": 45,
    "lowerLimit": 46
}

_ftr_quote_index = {
    "symbol": 0,
    "product": 1,
    "market": 2,
    "tradingDay": 3,
    "date": 4,
    "time": 5,
    "preClose": 6,
    "open": 7,
    "high": 8,
    "low": 9,
    "close": 10,
    "last": 11,
    "limitDown": 12,
    "limitUp": 13,
    "curVol": 14,
    "volume": 15,
    "curTurnover": 16,
    "turnover": 17,
    "oi": 18,
    "settle": 19,
    "preOI": 20,
    "prSettle": 21,
    "curDelta": 22,
    "preDelta": 23,
    "askPrice1": 24,
    "askPrice2": 25,
    "askPrice3": 26,
    "askPrice4": 27,
    "askPrice5": 28,
    "bidPrice1": 29,
    "bidPrice2": 30,
    "bidPrice3": 31,
    "bidPrice4": 32,
    "bidPrice5": 33,
    "askVolume1": 34,
    "askVolume2": 35,
    "askVolume3": 36,
    "askVolume4": 37,
    "askVolume5": 38,
    "bidVolume1": 39,
    "bidVolume2": 40,
    "bidVolume3": 41,
    "bidVolume4": 42,
    "bidVolume5": 43,
    "unixTime": 44
}


_stk_quote_index = {
    "symbol": 0,
    "market": 1,
    "date": 2,
    "time": 3,
    "preClose": 4,
    "open": 5,
    "high": 6,
    "low": 7,
    "last": 8,
    "numTrades": 9,
    "curNumTrades": 10,
    "volume": 11,
    "curVol": 12,
    "turnover": 13,
    "curTurnover": 14,
    "peratio1": 15,
    "peratio2": 16,
    "totalAskVolume": 17,
    "wavgAskPrice": 18,
    "askLevel": 19,
    "totalBidVolume": 20,
    "wavgBidPrice": 21,
    "bidLevel": 22,
    "iopv": 23,
    "ytm": 24,
    "askPrice1": 25,
    "askPrice2": 26,
    "askPrice3": 27,
    "askPrice4": 28,
    "askPrice5": 29,
    "askPrice6": 30,
    "askPrice7": 31,
    "askPrice8": 32,
    "askPrice9": 33,
    "askPrice10": 34,
    "bidPrice1": 35,
    "bidPrice2": 36,
    "bidPrice3": 37,
    "bidPrice4": 38,
    "bidPrice5": 39,
    "bidPrice6": 40,
    "bidPrice7": 41,
    "bidPrice8": 42,
    "bidPrice9": 43,
    "bidPrice10": 44,
    "askVolume1": 45,
    "askVolume2": 46,
    "askVolume3": 47,
    "askVolume4": 48,
    "askVolume5": 49,
    "askVolume6": 50,
    "askVolume7": 51,
    "askVolume8": 52,
    "askVolume9": 53,
    "askVolume10": 54,
    "bidVolume1": 55,
    "bidVolume2": 56,
    "bidVolume3": 57,
    "bidVolume4": 58,
    "bidVolume5": 59,
    "bidVolume6": 60,
    "bidVolume7": 61,
    "bidVolume8": 62,
    "bidVolume9": 63,
    "bidVolume10": 64,
    "unixTime": 65,
    "upperLimit": 66,
    "lowerLimit": 67
}


class Contract(object):
    def __init__(self, auto_load_ddb=False) -> None:
        self.opt_contract = {}
        self.ftr_contract = {}
        self.stk_contract = {}
        self.underlying_opt_contract = {}
        self.opt_underlying_total_count = {}
        self.opt_group_for_synthetic = {}

        if auto_load_ddb == True:
            self.load_contract_from_ddb()

    def load_contract_from_ddb(self) -> None:
        ddb_query = get_ddb_query()
        self.opt_contract, self.ftr_contract, self.stk_contract = ddb_query.query_contract()
        for symbol in self.opt_contract:
            if self.opt_contract[symbol]["underlyingCode"] not in self.underlying_opt_contract:
                self.underlying_opt_contract[self.opt_contract[symbol]["underlyingCode"]] = {}
            if self.opt_contract[symbol]["underlyingCode"] not in self.opt_underlying_total_count:
                self.opt_underlying_total_count[self.opt_contract[symbol]["underlyingCode"]] = 0
            if self.opt_contract[symbol]["underlyingCode"] not in self.opt_group_for_synthetic:
                self.opt_group_for_synthetic[self.opt_contract[symbol]["underlyingCode"]] = {}
            if self.opt_contract[symbol]["expireDate"] not in self.opt_group_for_synthetic[
                self.opt_contract[symbol]["underlyingCode"]]:
                self.opt_group_for_synthetic[self.opt_contract[symbol]["underlyingCode"]][
                    self.opt_contract[symbol]["expireDate"]] = {}
            if self.opt_contract[symbol]["strikePrice"] not in \
                    self.opt_group_for_synthetic[self.opt_contract[symbol]["underlyingCode"]][
                        self.opt_contract[symbol]["expireDate"]]:
                self.opt_group_for_synthetic[self.opt_contract[symbol]["underlyingCode"]][
                    self.opt_contract[symbol]["expireDate"]][self.opt_contract[symbol]["strikePrice"]] = {}

            self.underlying_opt_contract[self.opt_contract[symbol]["underlyingCode"]][symbol] = self.opt_contract[
                symbol]
            self.opt_underlying_total_count[self.opt_contract[symbol]["underlyingCode"]] += 1
            self.opt_group_for_synthetic[self.opt_contract[symbol]["underlyingCode"]][
                self.opt_contract[symbol]["expireDate"]][self.opt_contract[symbol]["strikePrice"]][
                self.opt_contract[symbol]["type"]] = self.opt_contract[symbol]


class OptQuoteData(object):
    def __init__(self) -> None:
        self.symbol_index = _opt_quote_index["symbol"]
        self.quote = {}
        self.lock = threading.Lock()

    @staticmethod
    def get_opt_quote_index() -> dict:
        return _opt_quote_index

    def update_quote(self, row: list) -> None:
        self.lock.acquire()
        self.quote[row[self.symbol_index]] = row
        self.lock.release()

    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_quote_with_symbol(self, symbol: str) -> list:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[symbol])
        self.lock.release()
        return res

class FtrQuoteData(object):
    def __init__(self) -> None:
        self.symbol_index = _ftr_quote_index["symbol"]
        self.last_price_index = _ftr_quote_index["last"]
        self.quote = {}
        self.lock = threading.Lock()

    @staticmethod
    def get_opt_quote_index() -> dict:
        return _ftr_quote_index

    def update_quote(self, row: list) -> None:
        self.lock.acquire()
        self.quote[row[self.symbol_index]] = row
        self.lock.release()

    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_quote_with_symbol(self, symbol: str) -> list:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[symbol])
        self.lock.release()
        return res

    def get_last_price_with_symbol(self, symbol: str) -> float:
        self.lock.acquire()
        res = self.quote[symbol][self.last_price_index]
        self.lock.release()
        return res

class StkQuoteData(object):
    def __init__(self) -> None:
        self.symbol_index = _stk_quote_index["symbol"]
        self.last_price_index = _stk_quote_index["last"]
        self.quote = {}
        self.lock = threading.Lock()

    @staticmethod
    def get_opt_quote_index() -> dict:
        return _stk_quote_index

    def update_quote(self, row: list) -> None:
        self.lock.acquire()
        self.quote[row[self.symbol_index]] = row
        self.lock.release()

    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_quote_with_symbol(self, symbol: str) -> list:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[symbol])
        self.lock.release()
        return res

    def get_last_price_with_symbol(self, symbol: str) -> float:
        self.lock.acquire()
        res = self.quote[symbol][self.last_price_index]
        self.lock.release()
        return res

class WingModelVolStreamData(object):
    def __init__(self) -> None:
        self.underlying_index = _wing_index["underlier"]
        self.update_time_index = _wing_index["update_time"]
        self.symbol_index = _wing_index["symbol"]
        self.delta_index = _wing_index["delta"]
        self.future_price_index = _wing_index["future_price"]
        self.expire_date_index = _wing_index["ExpireDate"]
        self.quote = {}
        self.lock = threading.Lock()
        self.best_future_price = {}

    def update_quote_bak(self, row: list) -> None:
        cur_underlying = row[self.underlying_index]
        cur_symbol = row[self.symbol_index]
        self.lock.acquire()
        if cur_underlying not in self.quote:
            self.quote[cur_underlying] = {}
        self.quote[cur_underlying][cur_symbol] = row
        self.lock.release()

    def get_quote_by_underlying_bak(self, underlying: str) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[underlying])
        self.lock.release()
        return res

    def get_quote_by_symbol_bak(self, underlying: str, symbol: str) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[underlying][symbol])
        self.lock.release()
        return res

    def get_quote_bak(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_delta_by_symbol_bak(self, underlying: str, symbol: str) -> float:
        self.lock.acquire()
        res = self.quote[underlying][symbol][self.delta_index]
        self.lock.release()
        return res
    # ------------------------------------------------------------------------------------------------------------------------
    def update_quote(self, row: list) -> None:
        self.lock.acquire()

        if row[self.symbol_index] not in self.quote:
            self.quote[row[self.symbol_index]] = {}
        self.quote[row[self.symbol_index]] = row

        if row[self.underlying_index] not in self.best_future_price:
            self.best_future_price[row[self.underlying_index]] = {}
        self.best_future_price[row[self.underlying_index]][row[self.expire_date_index]] = row[self.future_price_index]

        self.lock.release()

    def get_near_best_future_price(self) -> float:
        self.lock.acquire()
        price_dict: dict = self.best_future_price["510300"]
        sorted_expire_date = sorted(price_dict.keys())
        res = price_dict[sorted_expire_date[0]]
        self.lock.release()
        return res


    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_delta_by_symbol(self, symbol: str) -> float:
        self.lock.acquire()
        res = self.quote[symbol][self.delta_index]
        self.lock.release()
        return res

    def get_future_price_by_symbol(self, symbol: str) -> float:
        self.lock.acquire()
        res = self.quote[symbol][self.future_price_index]
        self.lock.release()
        return res








class IndexStreamData(object):
    def __init__(self) -> None:
        self.quote = {}
        self.lock = threading.Lock()


_contract = None
_wing_model_vol_stream_data = None
_opt_quote_data = None
_ftr_quote_data = None
_stk_quote_data = None


def get_contract() -> Contract:
    global _contract
    if not _contract:
        _contract = Contract(True)
    return _contract


def get_opt_quote_data() -> OptQuoteData:
    global _opt_quote_data
    if not _opt_quote_data:
        _opt_quote_data = OptQuoteData()
    return _opt_quote_data

def get_ftr_quote_data() -> FtrQuoteData:
    global _ftr_quote_data
    if not _ftr_quote_data:
        _ftr_quote_data = FtrQuoteData()
    return _ftr_quote_data

def get_stk_quote_data() -> StkQuoteData:
    global _stk_quote_data
    if not _stk_quote_data:
        _stk_quote_data = StkQuoteData()
    return _stk_quote_data


def get_wing_model_vol_stream_data() -> WingModelVolStreamData:
    global _wing_model_vol_stream_data
    if not _wing_model_vol_stream_data:
        _wing_model_vol_stream_data = WingModelVolStreamData()
    return _wing_model_vol_stream_data


if __name__ == '__main__':
    contract = get_contract()
    print(contract.opt_contract)

    # underlying_list = []
    # for underlying in contract.opt_group_for_synthetic:
    #     expire_date_list = []
    #     for expire_date in contract.opt_group_for_synthetic[underlying]:
    #         strike_price_list = []
    #         for strike_price in contract.opt_group_for_synthetic[underlying][expire_date]:
    #             strike_price_list.append(strike_price)
    #         expire_date_list.append({expire_date: strike_price_list})
    #     underlying_list.append({underlying: expire_date_list})
    #
    # print(underlying_list)