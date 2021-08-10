import logging
from dolphin_db.query_dolphin import get_ddb_query


class Contract(object):
    def __init__(self, auto_load_ddb=False) -> None:
        self.opt_contract = {}
        self.ftr_contract = {}
        self.stk_contract = {}
        if auto_load_ddb == True:
            self.load_contract_from_ddb()

    def load_contract_from_ddb(self) -> None:
        ddb_query = get_ddb_query()
        self.opt_contract, self.ftr_contract, self.stk_contract = ddb_query.query_contract()


_contract = None

def get_contract() -> Contract:
    global _contract
    if not _contract:
        _contract = Contract(True)
    return _contract
