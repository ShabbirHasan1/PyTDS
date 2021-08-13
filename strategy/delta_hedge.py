import numpy as np
import numba as nb
import pandas as pd
import logging
from trade_api.option_trade import get_option_trade
from config.config import get_app_config
from data.account_data import get_account
from data.wrapper_data import get_api_pool
from data.quote_data import get_contract


class DeltaHedge(object):
    def __init__(self) -> None:
        self.contract = get_contract()
        self.opt_contracts = self.contract.opt_contract
        self.ftr_contracts = self.contract.ftr_contract
        self.stk_contracts = self.contract.stk_contract

        self.api_pool = get_api_pool()
        self.accounts = get_account()
        self.app_config = get_app_config()
        self.option_trade = get_option_trade()

    def on_stream_received(self, row: list):
        pass



_delta_hedge = None

def get_delta_hedge() -> DeltaHedge:
    global _delta_hedge
    if not _delta_hedge:
        _delta_hedge = DeltaHedge()
    return _delta_hedge

if __name__ == '__main__':
    get_delta_hedge()