import pandas as pd
from trade_api.c_struct import *
import threading
import logging

_final_status = {"F", "T", "C", "B", "R"}


class TradeConfig(object):
    def __init__(self):
        pass


class OptOrderData(object):
    def __init__(self) -> None:
        self.order_data = {}
        self.lock = threading.Lock()

    def update_order(self, order: STesOptOrder) -> None:
        account = order.account.decode()
        symbol = order.symbol.decode()
        underlyingCode = order.underlyingCode.decode()
        orderRef = order.orderRef.decode()
        direction = order.direction.decode()
        offset = order.offset.decode()
        hedgeFlag = order.hedgeFlag.decode()
        price = order.price
        volume = order.volume
        createDate = order.createDate
        createTime = order.createTime
        entrustDate = order.entrustDate
        entrustTime = order.entrustTime
        updateTime = order.updateTime
        tradeVolume = order.tradeVolume
        orderStatus = order.orderStatus.decode()
        trackCode = order.trackCode.decode()
        self.lock.acquire()
        if orderStatus in _final_status:
            logging.warning("order time sequence warning, orderRef: {0}".format(orderRef))
            self.lock.release()
            return
        self.order_data[orderRef] = {
            "account": account,
            "symbol": symbol,
            "underlyingCode": underlyingCode,
            "direction": direction,
            "offset": offset,
            "hedgeFlag": hedgeFlag,
            "price": price,
            "volume": volume,
            "createDate": createDate,
            "createTime": createTime,
            "entrustDate": entrustDate,
            "entrustTime": entrustTime,
            "updateTime": updateTime,
            "tradeVolume": tradeVolume,
            "trackCode": trackCode
        }
        self.lock.release()
        logging.info(self.order_data)


class OptTradeData(object):
    def __init__(self) -> None:
        self.trade_data = []
        self.lock = threading.Lock()

    def update_trade(self, trade: STesOptTrade) -> None:
        account = trade.account.decode()
        symbol = trade.symbol.decode()
        underlyingCode = trade.underlyingCode.decode()
        direction = trade.direction.decode()
        offset = trade.offset.decode()
        hedgeFlag = trade.hedgeFlag.decode()
        tradePrice = trade.tradePrice
        tradeVolume = trade.tradeVolume
        tradeDate = trade.tradeDate
        tradeTime = trade.tradeTime

        self.lock.acquire()
        self.trade_data.append([
            account,
            symbol,
            underlyingCode,
            direction,
            offset,
            hedgeFlag,
            tradePrice,
            tradeVolume,
            tradeDate,
            tradeTime
        ])
        self.lock.release()


class OptPositionData(object):
    def __init__(self) -> None:
        self.position_data = {}
        self.lock = threading.Lock()

    def update_position(self, position: STesOptPosition) -> None:
        account = position.account.decode()
        symbol = position.symbol.decode()
        underlyingCode = position.underlyingCode.decode()
        posType = position.posType
        hedgeFlag = position.hedgeFlag
        totalPos = position.totalPos
        todayPos = position.todayPos
        frozenOpenPos = position.frozenOpenPos
        frozenClosePos = position.frozenClosePos
        frozenTodayClosePos = position.frozenTodayClosePos
        openVolume = position.openVolume
        openAmount = position.openAmount
        closeVolume = position.closeVolume
        closeAmount = position.closeAmount

        self.lock.acquire()
        key = account, symbol, posType, hedgeFlag
        self.position_data[key] = {
            "account": account,
            "symbol": symbol,
            "underlyingCode": underlyingCode,
            "posType": posType,
            "hedgeFlag": hedgeFlag,
            "totalPos": totalPos,
            "todayPos": todayPos,
            "frozenOpenPos": frozenOpenPos,
            "frozenClosePos": frozenClosePos,
            "frozenTodayClosePos": frozenTodayClosePos,
            "openVolume": openVolume,
            "openAmount": openAmount,
            "closeVolume": closeVolume,
            "closeAmount": closeAmount
        }
        self.lock.release()


class OptContractData(object):
    def __init__(self):
        pass


_opt_order_data = None
_opt_trade_data = None
_opt_position_data = None

def get_opt_order_data() -> OptOrderData:
    global _opt_order_data
    if not _opt_order_data:
        _opt_order_data = OptOrderData()
    return _opt_order_data

def get_opt_trade_data() -> OptTradeData:
    global _opt_trade_data
    if not _opt_trade_data:
        _opt_trade_data = OptTradeData()
    return _opt_trade_data

def get_opt_position_data() -> OptPositionData:
    global _opt_position_data
    if not _opt_position_data:
        _opt_position_data = OptPositionData()
    return _opt_position_data