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
        self.opt_contracts, self.ftr_contracts, self.stk_contracts = get_contract()
        self.api_pool = get_api_pool()
        self.accounts = get_account()
        self.app_config = get_app_config()
        self.option_trade = get_option_trade()

    def on_stream_received(self, row: list):

