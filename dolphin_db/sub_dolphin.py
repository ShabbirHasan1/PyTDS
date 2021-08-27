import logging
import threading
from config.config import get_app_config
import dolphindb as ddb
import socket
from strategy.delta_hedge import get_delta_hedge
from data.quote_data import get_wing_model_vol_stream_data, get_contract, get_opt_quote_data, get_ftr_quote_data, get_stk_quote_data


_test = set()

def check_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, int(port)))
        return True
    except socket.error:
        return False
    finally:
        if s:
            s.close()


class DdbSub(object):
    def __init__(self) -> None:
        self.app_config = get_app_config().config_dict
        self.session = None
        self.port = 12345
        self.init_session()
        self.option_quote = get_opt_quote_data()
        self.future_quote = get_ftr_quote_data()
        self.stock_quote = get_stk_quote_data()
        self.wing_data = get_wing_model_vol_stream_data()

    def init_session(self) -> None:
        if not self.session:
            self.session = ddb.session()
        while check_port_in_use(self.port):
            self.port += 1
        self.session.enableStreaming(self.port)

    def subscribe_option_quote(self) -> None:
        for option_quote_config in self.app_config["dolphin_config"]["option_quote"].values():
            self.session.subscribe(
                host=option_quote_config["ip"],
                port=option_quote_config["port"],
                tableName=option_quote_config["table_name"],
                actionName="",
                handler=self.option_quote_handler,
                offset=-1,
                resub=False,
                filter=None
            )
            logging.info("subscribe {0} successfully".format(option_quote_config["table_name"]))

    def unsubscribe_option_quote(self) -> None:
        for option_quote_config in self.app_config["dolphin_config"]["option_quote"].values():
            self.session.unsubscribe(
                host=option_quote_config["ip"],
                port=option_quote_config["port"],
                tableName=option_quote_config["table_name"],
                actionName="",
            )
            logging.info("unsubscribe {0} successfully".format(option_quote_config["table_name"]))

    def subscribe_future_quote(self) -> None:
        for future_quote_config in self.app_config["dolphin_config"]["future_quote"].values():
            self.session.subscribe(
                host=future_quote_config["ip"],
                port=future_quote_config["port"],
                tableName=future_quote_config["table_name"],
                actionName="",
                handler=self.future_quote_handler,
                offset=-1,
                resub=False,
                filter=None
            )
            logging.info("subscribe {0} successfully".format(future_quote_config["table_name"]))

    def unsubscribe_future_quote(self) -> None:
        for future_quote_config in self.app_config["dolphin_config"]["future_quote"].values():
            self.session.unsubscribe(
                host=future_quote_config["ip"],
                port=future_quote_config["port"],
                tableName=future_quote_config["table_name"],
                actionName="",
            )
            logging.info("unsubscribe {0} successfully".format(future_quote_config["table_name"]))

    def subscribe_stock_quote(self) -> None:
        for stock_quote_config in self.app_config["dolphin_config"]["stock_quote"].values():
            self.session.subscribe(
                host=stock_quote_config["ip"],
                port=stock_quote_config["port"],
                tableName=stock_quote_config["table_name"],
                actionName="",
                handler=self.stock_quote_handler,
                offset=-1,
                resub=False,
                filter=None
            )
            logging.info("subscribe {0} successfully".format(stock_quote_config["table_name"]))

    def unsubscribe_stock_quote(self) -> None:
        for stock_quote_config in self.app_config["dolphin_config"]["stock_quote"].values():
            self.session.unsubscribe(
                host=stock_quote_config["ip"],
                port=stock_quote_config["port"],
                tableName=stock_quote_config["table_name"],
                actionName="",
            )
            logging.info("unsubscribe {0} successfully".format(stock_quote_config["table_name"]))


    def subscribe_wing_model(self) -> None:
        for wing_config in self.app_config["dolphin_config"]["wing_model_vol_stream"]:
            self.session.subscribe(
                host=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["ip"],
                port=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["port"],
                tableName=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["table_name"],
                actionName="",
                handler=self.wing_model_handler,
                offset=-1,
                resub=False,
                filter=None
            )
            logging.info(
                "subscribe {0} successfully".format(
                    self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["table_name"]))

    def unsubscribe_wing_model(self) -> None:
        for wing_config in self.app_config["dolphin_config"]["wing_model_vol_stream"]:
            self.session.unsubscribe(
                host=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["ip"],
                port=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["port"],
                tableName=self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["table_name"],
                actionName="",
            )
            logging.info(
                "unsubscribe {0} successfully".format(
                    self.app_config["dolphin_config"]["wing_model_vol_stream"][wing_config]["table_name"]))

    def subscribe_index_stream(self) -> None:
        self.session.subscribe(
            host=self.app_config["dolphin_config"]["index_stream"]["ip"],
            port=self.app_config["dolphin_config"]["index_stream"]["port"],
            tableName=self.app_config["dolphin_config"]["index_stream"]["table_name"],
            actionName="",
            handler=self.index_stream_handler,
            offset=-1,
            resub=False,
            filter=None
        )
        logging.info(
            "subscribe {0} successfully".format(self.app_config["dolphin_config"]["index_stream"]["table_name"]))

    def unsubscribe_index_stream(self) -> None:
        self.session.unsubscribe(
            host=self.app_config["dolphin_config"]["index_stream"]["ip"],
            port=self.app_config["dolphin_config"]["index_stream"]["port"],
            tableName=self.app_config["dolphin_config"]["index_stream"]["table_name"],
            actionName="",
        )
        logging.info(
            "unsubscribe {0} successfully".format(self.app_config["dolphin_config"]["index_stream"]["table_name"]))

    def option_quote_handler(self, row: list) -> None:
        self.option_quote.update_quote(row)

    def future_quote_handler(self, row: list) -> None:
        self.future_quote.update_quote(row)

    def stock_quote_handler(self, row: list) -> None:
        self.stock_quote.update_quote(row)

    def index_stream_handler(self, row: list) -> None:
        pass

    def wing_model_handler(self, row: list) -> None:
        self.wing_data.update_quote(row)


_ddb_sub = None

def get_ddb_sub() -> DdbSub:
    global _ddb_sub
    if not _ddb_sub:
        _ddb_sub = DdbSub()
    return _ddb_sub


if __name__ == '__main__':
    s = get_ddb_sub()
    s.subscribe_wing_model()
    import time
    time.sleep(10)
    get_wing_model_vol_stream_data().get_near_best_future_price()
    threading.Event().wait()
