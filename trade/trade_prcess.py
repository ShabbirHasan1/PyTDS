from data.wrapper_data import ApiInfo, ApiPool
from data.trade_data import get_opt_order_data, get_opt_trade_data, get_opt_position_data
from trade_api.c_struct import *


class TradeProcess(object):
    def __init__(self) -> None:
        self.opt_order_data = get_opt_order_data()
        self.opt_trade_data = get_opt_trade_data()
        self.opt_position_data = get_opt_position_data()

    def save_order(self, order: STesOptOrder or STesFtrOrder or STesStkOrder) -> None:
        if isinstance(order, STesOptOrder):
            self.opt_order_data.update_order(order)

        # todo ftr stk
        elif isinstance(order, STesFtrOrder):
            pass
        elif isinstance(order, STesStkOrder):
            pass
        else:
            pass

    def save_trade(self, trade: STesOptTrade or STesFtrTrade or STesStkTrade) -> None:
        if isinstance(trade, STesOptTrade):
            self.opt_trade_data.update_trade(trade)

        # todo ftr stk
        elif isinstance(trade, STesFtrTrade):
            pass
        elif isinstance(trade, STesStkTrade):
            pass
        else:
            pass

    def save_position(self, position: STesOptPosition or STesFtrPosition or STesStkPosition) -> None:
        if isinstance(position, STesOptPosition):
            self.opt_position_data.update_position(position)

        # todo ftr stk
        elif isinstance(position, STesFtrPosition):
            pass
        elif isinstance(position, STesStkPosition):
            pass
        else:
            pass

_trade_process = None

def get_trade_process() -> TradeProcess:
    global _trade_process
    if not _trade_process:
        _trade_process = TradeProcess()
    return _trade_process