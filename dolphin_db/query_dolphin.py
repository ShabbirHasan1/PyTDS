import logging
import dolphindb as ddb
import pandas as pd


class DdbQuery(object):
    def __init__(self) -> None:
        pass

    def query_contract(self) -> tuple:
        session = ddb.session()
        session.connect("10.0.60.59", 8503)

        opt_contract_query = f"""
                dbPath = "/home/taoli/Quote/RtqBase/"
                tc = loadTable(database(dbPath), "optCode")
                select * from tc where Date=now().date()
                """
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
            )
            opt_contract_dict[cur_row["InstrumentID"]] = cur_contract

        ftr_contract_query = f"""
                        dbPath = "/home/taoli/Quote/RtqBase/"
                        tc = loadTable(database(dbPath), "ftrCode")
                        select * from tc where Date=now().date() and ExchangeID='CFFEX'
                        """
        ftr_contract: pd.DataFrame = session.run(ftr_contract_query)
        ftr_row_num = ftr_contract.shape[0]
        ftr_contract_dict = {}
        for row in range(ftr_row_num):
            cur_row = ftr_contract.loc[row]
            cur_contract = dict(
                symbol=cur_row["InstrumentID"],
                exchange=cur_row["ExchangeID"],
                name=cur_row["InstrumentName"],
                deliveryYear=cur_row["DeliveryYear"],
                deliveryMonth=cur_row["DeliveryMonth"],
                expireDate=cur_row["DeliveryYear"] * 100 + cur_row["DeliveryMonth"],
                priceTick=cur_row["PriceTick"],
            )
            ftr_contract_dict[cur_row["InstrumentID"]] = cur_contract

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

        session.close()
        del session

        if not opt_contract_dict:
            logging.warning("cannot find opt contract from ddb")

        if not ftr_contract_dict:
            logging.warning("cannot find ftr contract from ddb")

        if not stk_contract_dict:
            logging.warning("cannot find stk contract from ddb")

        return opt_contract_dict, ftr_contract_dict, stk_contract_dict


_ddb_query = None


def get_ddb_query() -> DdbQuery:
    global _ddb_query
    if not _ddb_query:
        _ddb_query = DdbQuery()
    return _ddb_query


