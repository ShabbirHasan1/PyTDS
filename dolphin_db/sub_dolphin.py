import logging
import threading
from config.config import get_app_config
import dolphindb as ddb
import socket
from strategy.delta_hedge import get_delta_hedge
from data.quote_data import get_wing_model_vol_stream_data, get_contract


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

    def init_session(self) -> None:
        if not self.session:
            self.session = ddb.session()
        while check_port_in_use(self.port):
            self.port += 1
        self.session.enableStreaming(self.port)

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

    def index_stream_handler(self, row: list) -> None:
        pass

    def wing_model_handler(self, row: list) -> None:
        wing = get_wing_model_vol_stream_data()
        wing.update_quote(row)


_ddb_sub = None


def get_ddb_sub() -> DdbSub:
    global _ddb_sub
    if not _ddb_sub:
        _ddb_sub = DdbSub()
    return _ddb_sub


if __name__ == '__main__':
    s = get_ddb_sub()
    s.subscribe_wing_model()
    threading.Event().wait()
