import logging
from data.account_data import get_account
from data.quote_data import get_contract
from trade_api.option_trade import get_option_trade
from dolphin_db.query_dolphin import get_ddb_query
import threading
import multiprocessing


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
# fp = logging.FileHandler(PathConfig.app_log_path + "log_" + str(datetime.datetime.now().date()) + ".txt", encoding='utf-8')
fs = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fs])

class TradeT(threading.Thread):
    def __init__(self, option_trade, q: multiprocessing.Queue):
        super(TradeT, self).__init__()
        self.option_trade = option_trade
        self.event = multiprocessing.Event()
        self.event.set()
        self.q = q

    def start(self):
        while self.event.is_set():
            if self.q.qsize() > 0:
                cur_data = self.q.get()
                print(cur_data)
            self.event.clear()
            self.event.wait()





class TradeP(multiprocessing.Process):
    def __init__(self):
        super(TradeP, self).__init__()
        # account = get_account("admin", "666666", "").accounts
        # opt_contract = get_contract().opt_contract
        # option_trade = get_option_trade()
        # option_trade.contract = opt_contract
        # option_trade.login_account(account["237"])
        # option_trade.login_account(account["222"])
        # threading.Event().wait()

    def start(self):
        account = get_account("admin", "666666", "").accounts
        opt_contract = get_contract().opt_contract
        option_trade = get_option_trade()
        option_trade.contract = opt_contract
        option_trade.login_account(account["237"])
        option_trade.login_account(account["222"])



if __name__ == '__main__':
    account = get_account("admin", "666666", "").accounts
    opt_contract = get_contract().opt_contract

    option_trade = get_option_trade()

    # p = TradeP()
    # p.start()
    t = threading.Thread(target=option_trade.login_account, args=(account["222"],))
    t.start()
    t.join()
    print(111)


    # option_trade.login_account(account["237"])
    # option_trade.login_account(account["222"])

    threading.Event().wait()

