from data.wrapper_data import get_api_pool
from trade_api.option_trade import get_option_trade
import zmq
import threading
import socket
import sys


def check_port_in_use(port: int, host: str='127.0.0.1') -> bool:
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


class ZmqServerThread(threading.Thread):
    def __init__(self):
        super(ZmqServerThread, self).__init__()

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:6666")
        while True:
            try:
                print("wait for client ...")
                msg = socket.recv()
                print("msg from client:", msg.decode())
                socket.send(msg)
            except Exception as e:
                print("zmq error:", e)
                sys.exit()



class TradeRequest(object):
    def __init__(self) -> None:
        self.option_trade = get_option_trade()

    def make_order(self, order: dict) -> None:
        opt_order_list = []
        ftr_order_list = []
        stk_order_list = []
        if order["trade_type"] == "opt":
            # todo: split or create priority order
            for order_info in opt_order_list:
                self.option_trade.entrust_order(order_info)

    def cancel_order(self, order: dict, chase_flag: bool = False) -> None:
        if order["trade_type"] == "opt":
            self.option_trade.cancel_order(order, chase_flag)

    def create_split_order_list(self, order: list) -> list:
        pass

    def create_priority_order_list(self, order: list) -> list:
        pass


_trade_request = None

def get_trade_operate() -> TradeRequest:
    global _trade_request
    if not _trade_request:
        _trade_request = TradeRequest()
    return _trade_request

if __name__ == '__main__':
    import datetime
    import time
    trade_operation = TradeRequest()
    # time.sleep(1)
    # context = zmq.Context()
    # socket = context.socket(zmq.REQ)
    # socket.connect("tcp://localhost:6666")
    # while True:
    #     print(222)
    #     cur_time = str(datetime.datetime.now())
    #     send_msg = "current time: " + cur_time
    #     # print(send_msg)
    #     socket.send(send_msg.encode())
    #     message = socket.recv()
    #     print("receive reply: ", message.decode('utf-8'))
    #     time.sleep(1)


