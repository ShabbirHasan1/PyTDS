import logging
from data.account_data import get_account
from data.quote_data import get_contract
from trade_api.option_trade import get_option_trade
from dolphin_db.query_dolphin import get_ddb_query


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
# fp = logging.FileHandler(PathConfig.app_log_path + "log_" + str(datetime.datetime.now().date()) + ".txt", encoding='utf-8')
fs = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fs])


if __name__ == '__main__':
    account = get_account("admin", "666666", "").accounts
    opt_contract = get_contract().opt_contract

    option_trade = get_option_trade()
    option_trade.login_account(account["222"])

    import threading
    threading.Event().wait()

