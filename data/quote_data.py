import logging

from data.trade_data import OptPositionData
from dolphin_db.query_dolphin import get_ddb_query
import threading
import copy

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

    def update_quote(self, row: list) -> None:
        self.lock.acquire()
        self.quote[row[self.symbol_index]] = row
        self.lock.release()

    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

class WingModelVolStreamData(object):
    def __init__(self) -> None:
        self.underlying_index = _wing_index["underlier"]
        self.update_time_index = _wing_index["update_time"]
        self.symbol_index = _wing_index["symbol"]
        self.quote = {}
        self.lock = threading.Lock()

    def update_quote(self, row: list) -> None:
        cur_underlying = row[self.underlying_index]
        cur_symbol = row[self.symbol_index]
        self.lock.acquire()
        if cur_underlying not in self.quote:
            self.quote[cur_underlying] = {}
        self.quote[cur_underlying][cur_symbol] = row
        self.lock.release()

    def get_quote(self) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote)
        self.lock.release()
        return res

    def get_quote_by_underlying(self, underlying: str) -> dict:
        self.lock.acquire()
        res = copy.deepcopy(self.quote[underlying])
        self.lock.release()
        return res


class IndexStreamData(object):
    def __init__(self) -> None:
        self.quote = {}
        self.lock = threading.Lock()


_contract = None
_wing_model_vol_stream_data = None
_opt_quote_data = None


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


def get_wing_model_vol_stream_data() -> WingModelVolStreamData:
    global _wing_model_vol_stream_data
    if not _wing_model_vol_stream_data:
        _wing_model_vol_stream_data = WingModelVolStreamData()
    return _wing_model_vol_stream_data


if __name__ == '__main__':
    contract = get_contract()
    underlying_list = []
    for underlying in contract.opt_group_for_synthetic:
        expire_date_list = []
        for expire_date in contract.opt_group_for_synthetic[underlying]:
            strike_price_list = []
            for strike_price in contract.opt_group_for_synthetic[underlying][expire_date]:
                strike_price_list.append(strike_price)
            expire_date_list.append({expire_date: strike_price_list})
        underlying_list.append({underlying: expire_date_list})

    print(underlying_list)