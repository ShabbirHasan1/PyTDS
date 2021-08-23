import logging
import dolphindb as ddb
import pandas as pd
from config.config import get_app_config


class DdbQuery(object):
    def __init__(self) -> None:
        self.app_config = get_app_config()

    def query_contract(self) -> tuple:
        session = ddb.session()
        ip = self.app_config.config_dict["dolphin_config"]["contract"]["option"]["ip"]
        port = self.app_config.config_dict["dolphin_config"]["contract"]["option"]["port"]
        db_path = self.app_config.config_dict["dolphin_config"]["contract"]["option"]["db_path"]
        table_name = self.app_config.config_dict["dolphin_config"]["contract"]["option"]["table_name"]
        session.connect(ip, port)

        opt_contract_query = f"""
                dbPath = %s
                tc = loadTable(database(dbPath), "%s")
                select * from tc where Date=now().date()
                """ % (db_path, table_name)
        opt_contract: pd.DataFrame = session.run(opt_contract_query)
        opt_row_num = opt_contract.shape[0]
        opt_contract_dict = {}
        call = (1, 49)
        for row in range(opt_row_num):
            cur_row = opt_contract.loc[row]
            cur_contract = dict(
                symbol=cur_row["InstrumentID"],
                exchange=cur_row["ExchangeID"],
                name=cur_row["InstrumentName"],
                underlyingCode=cur_row["UnderlyingInstrID"],
                type=1 if cur_row["OptionsType"] in call else 2,
                strikePrice=cur_row["StrikePrice"],
                deliveryYear=cur_row["DeliveryYear"],
                deliveryMonth=cur_row["DeliveryMonth"],
                expireDate=cur_row["DeliveryYear"] * 100 + cur_row["DeliveryMonth"],
                priceTick=cur_row["PriceTick"],
                multiple=cur_row["VolumeMultiple"]
            )
            opt_contract_dict[cur_row["InstrumentID"]] = cur_contract

        session.close()

        ip = self.app_config.config_dict["dolphin_config"]["contract"]["future"]["ip"]
        port = self.app_config.config_dict["dolphin_config"]["contract"]["future"]["port"]
        db_path = self.app_config.config_dict["dolphin_config"]["contract"]["future"]["db_path"]
        table_name = self.app_config.config_dict["dolphin_config"]["contract"]["future"]["table_name"]
        session.connect(ip, port)

        ftr_contract_query = f"""
                        dbPath = %s
                        tc = loadTable(database(dbPath), "%s")
                        select * from tc where Date=now().date() and ExchangeID='CFFEX'
                        """ % (db_path, table_name)
        ftr_contract: pd.DataFrame = session.run(ftr_contract_query)
        ftr_row_num = ftr_contract.shape[0]
        ftr_contract_dict = {}
        for row in range(ftr_row_num):
            cur_row = ftr_contract.loc[row]
            if not cur_row["InstrumentID"].startswith("IC") and not cur_row["InstrumentID"].startswith("IF") and not \
            cur_row["InstrumentID"].startswith("IH"):
                continue
            cur_contract = dict(
                symbol=cur_row["InstrumentID"],
                exchange=cur_row["ExchangeID"],
                ProductID=cur_row["ProductID"],
                name=cur_row["InstrumentName"],
                deliveryYear=cur_row["DeliveryYear"],
                deliveryMonth=cur_row["DeliveryMonth"],
                expireDate=cur_row["DeliveryYear"] * 100 + cur_row["DeliveryMonth"],
                priceTick=cur_row["PriceTick"],
                multiple=cur_row["VolumeMultiple"]
            )
            ftr_contract_dict[cur_row["InstrumentID"]] = cur_contract

        session.close()

        stk_contract_dict = {
            "510050": {
                "symbol": "510050",
                "exchange": "SH",
                "name": "50ETF",
                "priceTick": 0.001
            },
            "510300": {
                "symbol": "510300",
                "exchange": "SH",
                "name": "300ETF",
                "priceTick": 0.001
            },
            "159919": {
                "symbol": "159919",
                "exchange": "SZ",
                "name": "300ETF",
                "priceTick": 0.001
            }
        }

        del session

        if not opt_contract_dict:
            logging.warning("cannot find opt contract from ddb")

        if not ftr_contract_dict:
            logging.warning("cannot find ftr contract from ddb")

        if not stk_contract_dict:
            logging.warning("cannot find stk contract from ddb")

        return opt_contract_dict, ftr_contract_dict, stk_contract_dict

    def query_option_quote(self) -> list:
        res = []
        session = ddb.session()
        for config in self.app_config.config_dict["dolphin_config"]["option_quote"].values():
            ip = config["ip"]
            port = config["port"]
            table_name = config["table_name"]
            session.connect(ip, port)
            recent_opt_quote_data: pd.DataFrame = session.run("select top 1 * from {0} context by symbol csort time desc".format(table_name))
            row_num = recent_opt_quote_data.shape[0]
            for row in range(row_num):
                row_data = recent_opt_quote_data.loc[row]
                res.append(row_data.tolist())
            session.close()
        del session
        return res


    def query_wing_data(self) -> list:
        res = []
        session = ddb.session()
        for config in self.app_config.config_dict["dolphin_config"]["wing_model_vol_stream"].values():
            ip = config["ip"]
            port = config["port"]
            table_name = config["table_name"]
            session.connect(ip, port)
            recent_wing_data: pd.DataFrame = session.run("select top 1 * from {0} context by symbol csort time desc".format(table_name))
            row_num = recent_wing_data.shape[0]
            for row in range(row_num):
                row_data = recent_wing_data.loc[row]
                res.append(row_data.tolist())
            session.close()
        del session
        return res


_ddb_query = None


def get_ddb_query() -> DdbQuery:
    global _ddb_query
    if not _ddb_query:
        _ddb_query = DdbQuery()
    return _ddb_query


if __name__ == '__main__':
    # opt_contract_dict, ftr_contract_dict, stk_contract_dict = DdbQuery().query_contract()
    # print(len(opt_contract_dict))
    # # print(ftr_contract_dict)
    import time
    t = time.time()
    d = get_ddb_query().query_wing_data()
    print(time.time() - t)


