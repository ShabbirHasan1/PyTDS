from ctypes import *

"""TES API STRUCTURES"""


def create_object(c_class, data: dict) -> Structure:
    ob = c_class()
    fields = ob._fields_
    attrs = []
    for field in fields:
        attrs.append(field[0])
    for k in data:
        if k in attrs:
            if isinstance(data[k], int):
                setattr(ob, k, data[k])
            elif isinstance(data[k], float):
                setattr(ob, k, data[k])
            elif isinstance(data[k], str):
                setattr(ob, k, data[k].encode())
            else:
                if k == "error":
                    error = create_object(STesError, data[k])
                    setattr(ob, k, pointer(error))
                else:
                    pass
        else:
            print("no default attribute: " + k)
            pass
    return ob


def get_data(ob: Structure) -> dict:
    result = {}
    fields = ob._fields_
    attrs = []
    for field in fields:
        attrs.append(field[0])
    for attr in attrs:
        value = getattr(ob, attr)
        if isinstance(value, int):
            result[attr] = value
        elif isinstance(value, float):
            result[attr] = value
        elif isinstance(value, bytes):
            if attr == "name":
                result[attr] = value.decode("gbk")
            else:
                try:
                    result[attr] = value.decode()
                except Exception as e:
                    print("utf-8解码失败，尝试gbk", str(e))
                    try:
                        result[attr] = value.decode("gbk")
                    except Exception as e:
                        print("gbk解码失败", str(e))

        else:
            if attr == "error":
                result[attr] = dict(
                    errid=value.errid,
                    category=value.category,
                    msg=value.msg.decode("gbk")
                )

            else:
                pass

    return result


# TES系统错误信息
class STesError(Structure):
    _pack_ = 1
    _fields_ = [
        # 错误代码
        ("errid", c_uint32),
        # 错误类别
        ("category", c_uint32),
        # 错误信息
        ("msg", c_char * 257)
    ]


# 虚拟交易账号登录响应
class STesRspLogin(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 客户端连接ID，如本地直连则为0
        ("clientID", c_uint64),
        # 交易日
        ("tradingDay", c_uint32),
        # 登录日期
        ("loginDate", c_uint32),
        # 登录时间
        ("loginTime", c_uint32)
    ]


# 虚拟交易账号登出响应
class STesRspLogout(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 客户端ID，如本地直连则为0
        ("clientID", c_uint64),
        # 登出日期
        ("logoutDate", c_uint32),
        # 登出时间
        ("logoutTime", c_uint32)
    ]


# 用户终端系统信息（上报用）
class STesUserSystemInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ("infoLength", c_uint32),
        ("systemInfo", c_char * 513),
        ("clientIP", c_char * 16),
        ("clientPort", c_uint16),
        ("clientAppID", c_char * 31),
        ("loginTime", c_uint32)
    ]


"""TES FTR API STRUCTURES"""


# 期货委托报单
class STesFtrEntrustOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 价格
        ("price", c_double),
        # 数量
        ("volume", c_int32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性
        ("orderID", c_uint32),
        # 追踪代码，客户端自行维护，字符串类型
        ("trackCode", c_char * 129)
    ]


# 期货委托撤单，支持三种方式，任选其一
class STesFtrCancelOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用，物理账号下报单的唯一索引，可以使用orderRef直接撤单，系统重启也不会改变
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性（在TES不重启情况下可使用）
        ("orderID", c_uint32),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单系统编号（交易所编号），使用exchange + orderSysID也可以撤单
        ("orderSysID", c_char * 33)
    ]


# 期货资金账户
class STesFtrCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 上次结算准备金
        ("preBalance", c_double),
        # 入金金额
        ("deposit", c_double),
        # 出金金额
        ("withdraw", c_double),
        # 当前保证金总额
        ("usedMargin", c_double),
        # 手续费
        ("commission", c_double),
        # 资金差额
        ("cashIn", c_double),
        # 平仓盈亏
        ("closeProfit", c_double),
        # 持仓盈亏
        ("positionProfit", c_double),
        # 冻结的资金
        ("frozenCash", c_double),
        # 冻结的保证金
        ("frozenMargin", c_double),
        # 冻结的手续费
        ("frozenCommission", c_double),
        # 期货结算准备金
        ("balance", c_double),
        # 可用资金
        ("available", c_double),
        # 可取资金
        ("withdrawable", c_double)
    ]


# 期货合约信息
class STesFtrContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 合约名称
        ("name", c_char * 33),
        # 交割年份
        ("deliveryYear", c_int16),
        # 交割月
        ("deliveryMonth", c_int8),
        # 上市日
        ("openDate", c_uint32),
        # 到期日
        ("expireDate", c_uint32),
        # 合约乘数
        ("multiple", c_int32),
        # 最小变动价位
        ("priceTick", c_double),
        # 多头保证金率
        ("longMarginRatio", c_double),
        # 空头保证金率
        ("shortMarginRatio", c_double),

        # added @20210317
        # 涨停价
        ("upperLimitPrice", c_double),
        # 跌停价
        ("lowerLimitPrice", c_double),
        # 前结算价
        ("preSettlementPrice", c_double)
    ]


# 期货委托回报
class STesFtrOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 经纪公司代码
        ("brokerID", c_char * 17),
        # 投资者代码
        ("investorID", c_char * 17),
        # 用户代码
        ("userID", c_char * 17),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 委托价格
        ("price", c_double),
        # 委托数量
        ("volume", c_int32),
        # 交易日
        ("tradingDay", c_uint32),
        # 创建日期
        ("createDate", c_uint32),
        # 创建时间（本地）
        ("createTime", c_uint32),
        # 委托日期（服务器）
        ("entrustDate", c_uint32),
        # 委托时间（服务器）
        ("entrustTime", c_uint32),
        # 最新更新时间（服务器）
        ("updateTime", c_uint32),
        # 成交数量
        ("tradeVolume", c_int32),
        # 委托状态
        ("orderStatus", c_char),
        # 撤单状态
        ("orderCancelStatus", c_char),
        # 报单本地编号（由柜台提供）
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 经纪公司报单编号（部分柜台）
        ("brokerSeq", c_uint32),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 错误代码与错误信息
        ("error", STesError),
        # 成交金额
        ("tradeAmount", c_double),
        # 手续费（含委托费等）
        ("commission", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32)
    ]

    # def get_data(self):
    #     result = {
    #         "account": self.account.decode(),
    #         "symbol": self.symbol.decode(),
    #         "exchange": self.exchange.decode(),
    #         "sessionID": self.sessionID.decode(),
    #         "brokerID": self.brokerID.decode(),
    #         "investorID": self.investorID.decode(),
    #         "userID": self.userID.decode(),
    #         "orderRef": self.orderRef.decode(),
    #         "orderPriceType": self.orderPriceType.decode(),
    #         "direction": self.direction.decode(),
    #         "offset": self.offset.decode(),
    #         "hedgeFlag": self.hedgeFlag,
    #         "price": self.price,
    #         "volume": self.volume,
    #         "tradingDay": self.tradingDay,
    #         "createDate": self.createDate,
    #         "createTime": self.createTime,
    #         "entrustDate": self.entrustDate,
    #         "entrustTime": self.entrustTime,
    #         "updateTime": self.updateTime,
    #         "tradeVolume": self.tradeVolume,
    #         "orderStatus": self.orderStatus.decode(),
    #         "orderCancelStatus": self.orderCancelStatus.decode(),
    #         "orderLocalID": self.orderLocalID.decode(),
    #         "orderSysID": self.orderSysID.decode(),
    #         "brokerSeq": self.brokerSeq,
    #         "reqID": self.reqID,
    #         "trackCode": self.trackCode.decode(),
    #         "error": {
    #             self.error.get_data()
    #         },
    #         "tradeAmount": self.tradeAmount,
    #         "commission": self.commission,
    #         "clientID": self.clientID,
    #         "orderID": self.orderID
    #     }
    #     return result

    # @classmethod
    # def create_order(cls, data: dict):
    #     order: STesFtrOrder = cls(
    #         account=data["account"].encode(),
    #         symbol=data["symbol"].encode(),
    #         exchange=data["exchange"].encode(),
    #         brokerID=data["brokerID"].encode(),
    #         investorID=data["investorID"].encode(),
    #         userID=data["userID"].encode(),
    #         orderRef=data["orderRef"].encode(),
    #         orderPriceType=data["orderPriceType"].encode(),
    #         direction=data["direction"].encode(),
    #         offset=data["offset"].encode(),
    #         hedgeFlag=data["hedgeFlag"],
    #         price=data["price"],
    #         volume=data["volume"],
    #         tradingDay=data["tradingDay"],
    #         createDate=data["createDate"],
    #         createTime=data["createTime"],
    #         entrustDate=data["entrustDate"],
    #         entrustTime=data["entrustTime"],
    #         updateTime=data["updateTime"],
    #         tradeVolume=data["tradeVolume"],
    #         orderStatus=data["orderStatus"].encode(),
    #         orderCancelStatus=data["orderCancelStatus"].encode(),
    #         orderLocalID=data["orderLocalID"].encode(),
    #         orderSysID=data["orderSysID"].encode(),
    #         brokerSeq=data["brokerSeq"],
    #         reqID=data["reqID"],
    #         trackCode=data["trackCode"],
    #
    #     )
    #     return order

    # @classmethod
    # def create_order(cls, data: dict):
    #     order = cls()
    #     for k in data:
    #         if isinstance(data[k], int):
    #             setattr(order, k, data[k])


# 期货成交回报
class STesFtrTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 成交价格
        ("tradePrice", c_double),
        # 成交数量
        ("tradeVolume", c_int32),
        # 成交金额
        ("tradeAmount", c_double),
        # 成交日期
        ("tradeDate", c_uint32),
        # 成交时间
        ("tradeTime", c_uint32),
        # 报单本地编号
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 成交系统编号（交易所编号）
        ("tradeSysID", c_char * 33),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 成交手续费
        ("commission", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32)
    ]

    # def get_data(self):
    #     result = {
    #         "account": self.account.decode(),
    #         "symbol": self.symbol.decode(),
    #         "exchange": self.exchange.decode(),
    #         "sessionID": self.sessionID.decode(),
    #         "orderRef": self.orderRef.decode(),
    #         "direction": self.direction.decode(),
    #         "offset": self.offset.decode(),
    #         "hedgeFlag": self.hedgeFlag,
    #         "tradePrice": self.tradePrice,
    #         "tradeVolume": self.tradeVolume,
    #         "tradeAmount": self.tradeAmount,
    #         "tradeDate": self.tradeDate,
    #         "tradeTime": self.tradeTime,
    #         "orderLocalID": self.orderLocalID.decode(),
    #         "orderSysID": self.orderSysID.decode(),
    #         "tradeSysID": self.tradeSysID.decode(),
    #         "reqID": self.reqID,
    #         "trackCode": self.trackCode.decode(),
    #         "commission": self.commission,
    #         "clientID": self.clientID,
    #         "orderID": self.orderID,
    #     }
    #     return result


# 期货持仓
class STesFtrPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 持仓类型
        ("posType", c_uint32),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 持仓日期
        ("posDate", c_uint32),
        # 当前总持仓
        ("totalPos", c_int32),
        # 今仓数量
        ("todayPos", c_int32),
        # 开仓冻结数量
        ("frozenOpenPos", c_int32),
        # 平仓冻结数量
        ("frozenClosePos", c_int32),
        # 平今冻结数量，仅对上期所合约有意义，对其他合约无意义
        ("frozenTodayClosePos", c_int32),
        # 今日开仓数量
        ("openVolume", c_int32),
        # 今日平仓数量
        ("closeVolume", c_int32),
        # 今日开仓金额
        ("openAmount", c_double),
        # 今日平仓金额
        ("closeAmount", c_double),
        # 持仓成本
        ("posCost", c_double),
        # 开仓成本
        ("openCost", c_double),
        # 保证金占用
        ("usedMargin", c_double),
        # 手续费
        ("commission", c_double),
        # 平仓盈亏
        ("closeProfit", c_double),
        # 持仓盈亏
        ("positionProfit", c_double),
        # 平今手续费平仓数量，用于计算手续费
        ("closeTodayVolume", c_int32),
        # 交易所代码
        ("exchange", c_char * 9)
    ]


# 期货查询报单
class STesFtrQueryOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID
        ("orderID", c_uint32),
        # 合约
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单状态
        ("orderStatus", c_char)
    ]


# 期货查询成交
class STesFtrQueryTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID
        ("orderID", c_uint32),
        # 合约
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
    ]


# 期货查询持仓
class STesFtrQueryPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 持仓类型
        ("posType", c_uint32)
    ]


# 期货查询合约
class STesFtrQueryContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
    ]


# 期货查询资金
class STesFtrQueryCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
    ]


"""TES OPT API STRUCTURES"""


# 期权委托报单
class STesOptEntrustOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 原始代码 symbol与originCode二选一，填一个即可
        ("originCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 价格
        ("price", c_double),
        # 数量
        ("volume", c_int32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性
        ("orderID", c_uint32),
        # 追踪代码，客户端自行维护，字符串类型
        ("trackCode", c_char * 129)
    ]


# 期权委托撤单，支持三种方式，任选其一
class STesOptCancelOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用，物理账号下报单的唯一索引，可以使用orderRef直接撤单，系统重启也不会改变
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性（在TES不重启情况下可使用）
        ("orderID", c_uint32),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单系统编号（交易所编号），使用exchange + orderSysID也可以撤单
        ("orderSysID", c_char * 33)
    ]


# 期权资金账户
class STesOptCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 上次结算准备金
        ("preBalance", c_double),
        # 入金金额
        ("deposit", c_double),
        # 出金金额
        ("withdraw", c_double),
        # 当前保证金总额
        ("usedMargin", c_double),
        # 手续费
        ("commission", c_double),
        # 资金差额
        ("cashIn", c_double),
        # 平仓盈亏
        ("closeProfit", c_double),
        # 持仓盈亏
        ("positionProfit", c_double),
        # 冻结的资金
        ("frozenCash", c_double),
        # 冻结的保证金
        ("frozenMargin", c_double),
        # 冻结的手续费
        ("frozenCommission", c_double),
        # 期货结算准备金
        ("balance", c_double),
        # 可用资金
        ("available", c_double),
        # 可取资金
        ("withdrawable", c_double)
    ]


# 期权合约信息
class STesOptContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 合约名称
        ("name", c_char * 33),
        # 原始代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 产品代码
        ("productID", c_char * 17),
        # 期权类型
        ("type", c_uint32),
        # 执行价
        ("strikePrice", c_double),
        # 交割年份
        ("deliveryYear", c_int16),
        # 交割月
        ("deliveryMonth", c_int8),
        # 上市日
        ("openDate", c_uint32),
        # 到期日
        ("expireDate", c_uint32),
        # 合约乘数
        ("multiple", c_int32),
        # 最小变动价位
        ("priceTick", c_double),
        # 市价单最大下单量
        ("maxMarketVolume", c_int32),
        # 市价单最小下单量
        ("minMarketVolume", c_int32),
        # 限价单最大下单量
        ("maxLimitVolume", c_int32),
        # 限价单最小下单量
        ("minLimitVolume", c_int32),
        # 合约交易状态
        ("status", c_char),
        # 涨停价
        ("upperLimitPrice", c_double),
        # 跌停价
        ("lowerLimitPrice", c_double),
        # 昨收盘价
        ("preClosePrice", c_double),
        # 昨结算价
        ("preSettlementPrice", c_double)
    ]


# 期权委托回报
class STesOptOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 经纪公司代码
        ("brokerID", c_char * 17),
        # 投资者代码
        ("investorID", c_char * 17),
        # 用户代码
        ("userID", c_char * 17),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 委托价格
        ("price", c_double),
        # 委托数量
        ("volume", c_int32),
        # 交易日
        ("tradingDay", c_uint32),
        # 创建日期
        ("createDate", c_uint32),
        # 创建时间（本地）
        ("createTime", c_uint32),
        # 委托日期（服务器）
        ("entrustDate", c_uint32),
        # 委托时间（服务器）
        ("entrustTime", c_uint32),
        # 最新更新时间（服务器）
        ("updateTime", c_uint32),
        # 成交数量
        ("tradeVolume", c_int32),
        # 委托状态
        ("orderStatus", c_char),
        # 撤单状态
        ("orderCancelStatus", c_char),
        # 报单本地编号（由柜台提供）
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 经纪公司报单编号（部分柜台）
        ("brokerSeq", c_uint32),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 错误代码与错误信息
        ("error", STesError),
        # 成交金额
        ("tradeAmount", c_double),
        # 手续费（含委托费等）
        ("commission", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32)
    ]


# 期权成交回报
class STesOptTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 买卖方向
        ("direction", c_char),
        # 开平标志
        ("offset", c_char),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 成交价格
        ("tradePrice", c_double),
        # 成交数量
        ("tradeVolume", c_int32),
        # 成交金额
        ("tradeAmount", c_double),
        # 成交日期
        ("tradeDate", c_uint32),
        # 成交时间
        ("tradeTime", c_uint32),
        # 报单本地编号
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 成交系统编号（交易所编号）
        ("tradeSysID", c_char * 33),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 成交手续费
        ("commission", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32)
    ]


# 期权持仓
class STesOptPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟期货交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 持仓类型
        ("posType", c_uint32),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 持仓日期
        ("posDate", c_uint32),
        # 当前总持仓
        ("totalPos", c_int32),
        # 今仓数量
        ("todayPos", c_int32),
        # 开仓冻结数量
        ("frozenOpenPos", c_int32),
        # 平仓冻结数量
        ("frozenClosePos", c_int32),
        # 平今冻结数量，仅对上期所合约有意义，对其他合约无意义
        ("frozenTodayClosePos", c_int32),
        # 今日开仓数量
        ("openVolume", c_int32),
        # 今日开仓金额
        ("openAmount", c_double),
        # 今日平仓数量
        ("closeVolume", c_int32),
        # 今日平仓金额
        ("closeAmount", c_double),
        # 持仓成本
        ("posCost", c_double),
        # 开仓成本
        ("openCost", c_double),
        # 保证金占用
        ("usedMargin", c_double),
        # 手续费
        ("commission", c_double),
        # 平仓盈亏
        ("closeProfit", c_double),
        # 持仓盈亏
        ("positionProfit", c_double),
        # 平今手续费平仓数量，用于计算手续费
        ("closeTodayVolume", c_int32),
    ]


# 期权行情信息
class STesOptQuoteData(Structure):
    _pack_ = 1
    _fields_ = [
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始合约代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 交易日
        ("tradingDay", c_uint32),
        # 最新价
        ("lastPrice", c_double),
        # 昨收盘价
        ("preClose", c_double),
        # 昨结算价
        ("preSettlement", c_double),
        # 开盘价
        ("openPrice", c_double),
        # 最高价
        ("highPrice", c_double),
        # 最低价
        ("lowPrice", c_double),
        # 收盘价
        ("closePrice", c_double),
        # 数量
        ("volume", c_int32),
        # 持仓量
        ("openInterest", c_int32),
        # 昨持仓量
        ("preOpenInterest", c_int32),
        # 成交金额
        ("turnover", c_double),
        # 涨停价
        ("upperLimit", c_double),
        # 跌停价
        ("lowerLimit", c_double),
        # 最新更新时间（服务器）
        ("updateTime", c_uint32),
        # 行情深度
        ("levelDepth", c_uint32),
        # 买价
        ("bidPrice[LEVEL_5]", c_double),
        # 买量
        ("bidVolume[LEVEL_5]", c_int32),
        # 卖价
        ("askPrice[LEVEL_5]", c_double),
        # 卖量
        ("askVolume[LEVEL_5]", c_int32)
    ]


# 期权合约状态变化信息
class STesOptContractStatusChange(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始合约代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 进入状态时间
        ("enterTime", c_uint32),
        # 合约交易状态
        ("status", c_char),
        # 进入状态原因
        ("reason", c_char)
    ]


# 期权查询报单
class STesOptQueryOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID
        ("orderID", c_uint32),
        # 合约
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单状态
        ("orderStatus", c_char)
    ]


# 期权查询成交
class STesOptQueryTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID
        ("orderID", c_uint32),
        # 合约
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
    ]


# 期权查询持仓
class STesOptQueryPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 持仓类型
        ("posType", c_uint32),
        # 期权类型
        ("type", c_uint32)
    ]


# 期权查询合约
class STesOptQueryContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 原始合约代码
        ("originCode", c_char * 33),
        # 基础合约代码
        ("underlyingCode", c_char * 33),
        # 期权类型
        ("type", c_uint32)
    ]


# 期权查询行情
class STesOptQueryQuote(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
    ]


# 期权查询资金
class STesOptQueryCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
    ]


# 股票期权备兑锁定证券请求
class STesOptLockRequest(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 期权合约代码
        ("symbol", c_char * 33),
        # 基础证券代码
        ("stockCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 锁定标志
        ("lockFlag", c_char),
        # 数量, 若填写symbol，实际锁定证券数量需乘以合约乘数；若填写stockCode，保持不变
        ("volume", c_int32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性
        ("orderID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129)
    ]


# 股票期权备兑锁定委托
class STesOptLockOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 证券代码
        ("stockCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 经纪公司代码
        ("brokerID", c_char * 17),
        # 投资者代码
        ("investorID", c_char * 17),
        # 用户代码
        ("userID", c_char * 17),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 锁定标志
        ("lockFlag", c_char),
        # 数量
        ("volume", c_int32),
        # 交易日
        ("tradingDay", c_uint32),
        # 创建日期（本地）
        ("createDate", c_uint32),
        # 创建时间（本地）
        ("createTime", c_uint32),
        # 委托日期（服务器）
        ("entrustDate", c_uint32),
        # 委托时间（服务器）
        ("entrustTime", c_uint32),
        # 最新更新时间（服务器）
        ("updateTime", c_uint32),
        # 委托状态
        ("orderStatus", c_char),
        # 委托本地编号
        ("orderLocalID", c_char * 33),
        # 委托系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 经纪公司锁定序列号
        ("brokerSeq", c_uint32),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32),
        # 错误代码与错误信息
        ("error", STesError)
    ]


# 股票期权备兑锁定委托查询
class STesOptQueryLockOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_char),
        # 报单ID
        ("orderID", c_uint32),
        # 备兑证券代码
        ("stockCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单状态
        ("orderStatus", c_char)
    ]


# 股票期权备兑证券仓位
class STesOptLockPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 证券代码
        ("stockCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 已锁定持仓数量（含已备兑开仓数量、可解锁数量、委托冻结数量）lockedPos = coveredPos + unlockablePos + frozenPos
        ("lockedPos", c_int32),
        # 已备兑开仓数量
        ("coveredPos", c_int32),
        # 可解锁数量
        ("unlockablePos", c_int32),
        # 委托冻结数量
        ("frozenPos", c_int32),
        # 可锁定持仓数量，接口不支持获取，值固定为0
        ("lockablePos", c_int32)
    ]


# 查询股票期权备兑证券仓位
class STesOptQueryLockPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 证券代码
        ("stockCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9)
    ]


# 期权行权请求
class STesOptEntrustExecOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 原始代码
        ("originCode", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 数量
        ("volume", c_int32),
        # 投机套保标志
        ("hedgeFlag", c_uint32),
        # 开平标志
        ("offset", c_char),
        # 行权类型
        ("exerciseType", c_char),
        # 行权后是否保留期货头寸（上期所已废弃） CFFEX:No;DCE/CZCE:Yes;SHFE:Yes/No
        ("reservePositionFlag", c_char),
        # 行权后期货头寸是否自动平仓 CFFEX:Yes;DCE/CZCE:No;SHFE:Yes/No
        ("autoCloseFlag", c_char),
        # 行权后期货头寸保留方向
        ("posType", c_uint32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性
        ("orderID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129)
    ]


# 期权行权撤单请求
STesOptCancelExecOrder = STesOptCancelOrder


# 期权行权委托查询
class STesOptQueryExecOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID
        ("orderID", c_uint32),
        # 合约
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 执行状态
        ("exerciseStatus", c_char)
    ]


# 期权行权委托回报
class STesOptExecOrder(Structure):
    _pack_ = 1
    _fields_ = [
        ("account", c_char * 33),
        ("symbol", c_char * 33),
        ("exchange", c_char * 9),
        ("originCode", c_char * 33),
        ("underlyingCode", c_char * 33),
        ("sessionID", c_char * 22),
        ("brokerID", c_char * 17),
        ("investorID", c_char * 17),
        ("userID", c_char * 17),
        ("orderRef", c_char * 35),
        ("volume", c_int32),
        ("hedgeFlag", c_uint32),
        ("offset", c_char),
        ("exerciseType", c_char),
        ("reservePositionFlag", c_char),
        ("autoCloseFlag", c_char),
        ("posType", c_uint32),
        ("tradingDay", c_uint32),
        ("createDate", c_uint32),
        ("createTime", c_uint32),
        ("entrustDate", c_uint32),
        ("entrustTime", c_uint32),
        ("updateTime", c_uint32),
        ("exerciseStatus", c_char),
        ("orderCancelStatus", c_char),
        ("commission", c_double),
        ("orderLocalID", c_char * 33),
        ("orderSysID", c_char * 33),
        ("brokerSeq", c_uint32),
        ("reqID", c_uint32),
        ("clientID", c_uint64),
        ("orderID", c_uint32),
        ("trackCode", c_char * 129),
        ("error", STesError),
    ]


"""TES STK API STRUCTURES"""


# 证券委托报单
class STesStkEntrustOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 子账户类型 LTS需要，其他可不填
        ("type", c_uint32),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 价格
        ("price", c_double),
        # 数量
        ("volume", c_int32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性
        ("orderID", c_uint32),
        # 追踪代码，客户端自行维护，字符串类型
        ("trackCode", c_char * 129)
    ]


# 证券撤单，支持多种方式
class STesStkCancelOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用，物理账号下报单的唯一索引，可以使用orderRef直接撤单，系统重启也不会改变
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 客户端报单流水号，客户端自行维护，clientID + orderID应保证唯一性（在TES不重启情况下可使用）
        ("orderID", c_uint32),
        # 交易所代码
        ("exchange", c_char * 9),
        # 报单系统编号（交易所编号），使用exchange + orderSysID也可以撤单
        ("orderSysID", c_char * 33)
    ]


# 证券资金账户
class STesStkCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账号类型（普通、信用、衍生等）
        ("subAccountType", c_uint32),
        # 子账号（物理子账号，非虚拟子账号）
        ("subAccount", c_char * 33),
        # 入金金额
        ("deposit", c_double),
        # 出金金额
        ("withdraw", c_double),
        # 结算金额
        ("balance", c_double),
        # 可用金额
        ("available", c_double),
        # 可取金额
        ("withdrawable", c_double),
        # 冻结金额
        ("frozenCash", c_double),
        # 资金差额(当日卖出 - 买入)
        ("cashIn", c_double),
        # 手续费
        ("commission", c_double),
        # 过户费
        ("transferFee", c_double),
        # 印花税
        ("stampTax", c_double),
        # 冻结手续费
        ("frozenCommission", c_double),
        # 冻结过户费
        ("frozenTransferFee", c_double),
        # 冻结印花税
        ("frozenStampTax", c_double),
        # 前日金额
        ("preBalance", c_double)
    ]


# 证券合约信息
class STesStkContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 合约名称
        ("name", c_char * 33),
        # 产品代码，表示产品类型，如股票、基金、债券等，不同柜台接口取值不同
        # 将被废弃，由type取代
        ("productID", c_char * 17),
        # 合约乘数，对证券类基本无用，今后不再使用
        ("multiple", c_int32),
        # 最小变动价位
        ("priceTick", c_double),
        # 市价单最大下单量
        ("maxMarketOrderVolume", c_int32),
        # 市价单最小下单量
        ("minMarketOrderVolume", c_int32),
        # 限价单最大下单量
        ("maxLimitOrderVolume", c_int32),
        # 限价单最小下单量
        ("minLimitOrderVolume", c_int32),
        # 买下单单位
        ("buyUnit", c_int32),
        # 卖下单单位
        ("sellUnit", c_int32),
        # 市场代码，表示合约所处交易市场，部分柜台支持
        ("marketCode", c_char),
        # 今日涨停价，0代表停牌或不存在，部分柜台支持
        ("upperLimit", c_double),
        # 今日跌停价，0代表停牌或不存在，部分柜台支持
        ("lowerLimit", c_double),
        # 证券详细类型
        ("type", c_uint8),
        # 昨收盘价
        ("preClose", c_double),
        # 证券状态
        ("status", c_char)
    ]


# ETF合约信息
class STesStkEtfContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 申赎代码
        ("purRedCode", c_char * 33),
        # 最小申赎份数
        ("purRedUnitCount", c_int32),
        # 最大现金替代比例
        ("maxCashRatio", c_double),
        # 申购赎回状态
        ("status", c_char),
        # 篮子的预估现金差额
        ("estimateCash", c_double),
        # 单位净值
        ("netValue", c_double),
        # 基金类别
        ("type", c_char),
        # 前日现金差额
        ("cashComponent", c_double),
        # 申赎总净值金额
        ("totalAmount", c_double),
        # 成分股数量
        ("componentCount", c_int32)
    ]


# ETF成份股信息
class STesStkEtfComponent(Structure):
    _pack_ = 1
    _field = [
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 所属ETF组合代码
        ("etfComboCode", c_char * 33),
        # 成分股名称
        ("name", c_char * 33),
        # 股票数量
        ("volume", c_int32),
        # 现金替代标志
        ("replaceStatus", c_char),
        # 申购溢价比例
        ("premium", c_double),
        # 赎回折价比例
        ("discount", c_double),
        # 申购替代金额
        ("purchaseAmount", c_double),
        # 赎回替代金额
        ("redeemAmount", c_double)
    ]


# 证券委托回报
class STesStkOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账号（物理子账号，非虚拟子账号），仅对LTS有效
        ("subAccount", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 组合合约代码
        ("comboSymbol", c_char * 33),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 经纪公司代码
        ("brokerID", c_char * 17),
        # 投资者代码
        ("investorID", c_char * 17),
        # 用户代码
        ("userID", c_char * 17),
        # 报单引用，可用作同账号下报单的唯一索引
        ("orderRef", c_char * 35),
        # 报单报价类型
        ("orderPriceType", c_char),
        # 买卖方向
        ("direction", c_char),
        # 价格
        ("price", c_double),
        # 数量
        ("volume", c_int32),
        # 交易日
        ("tradingDay", c_uint32),
        # 创建日期
        ("createDate", c_uint32),
        # 创建时间（本地）
        ("createTime", c_uint32),
        # 委托日期（服务器）
        ("entrustDate", c_uint32),
        # 委托时间（服务器）
        ("entrustTime", c_uint32),
        # 最新更新时间（服务器）
        ("updateTime", c_uint32),
        # 成交数量
        ("tradeVolume", c_int32),
        # 成交金额
        ("tradeAmount", c_double),
        # 是否ETF
        ("isETF", c_bool),
        # 委托状态
        ("orderStatus", c_char),
        # 撤单状态
        ("orderCancelStatus", c_char),
        # 报单本地编号
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 经纪公司报单编号
        ("brokerSeq", c_uint32),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 错误代码与错误信息
        ("error", STesError),
        # 手续费
        ("commission", c_double),
        # 过户费
        ("transferFee", c_double),
        # 印花税
        ("stampTax", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32),
        # 批次ID，由客户在批量委托时提供，非批量情况下默认为0
        ("batchID", c_uint32)
    ]


# 证券成交回报
class STesStkTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账号（物理子账号，非虚拟子账号），仅对LTS有效
        ("subAccount", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 组合合约代码
        ("comboSymbol", c_char * 33),
        # 会话连接号
        ("sessionID", c_char * 22),
        # 报单引用（本地编号）
        ("orderRef", c_char * 35),
        # 买卖方向
        ("direction", c_char),
        # 成交价格
        ("tradePrice", c_double),
        # 成交数量
        ("tradeVolume", c_int32),
        # 成交金额
        ("tradeAmount", c_double),
        # 成交日期
        ("tradeDate", c_uint32),
        # 成交时间
        ("tradeTime", c_uint32),
        # 报单本地编号
        ("orderLocalID", c_char * 33),
        # 报单系统编号（交易所编号）
        ("orderSysID", c_char * 33),
        # 经纪公司报单编号
        ("brokerSeq", c_uint32),
        # 成交系统编号（交易所编号）
        ("tradeSysID", c_char * 33),
        # 请求流水号，客户端自行维护
        ("reqID", c_uint32),
        # 追踪代码
        ("trackCode", c_char * 129),
        # 是否ETF
        ("isETF", c_bool),
        # 手续费
        ("commission", c_double),
        # 过户费
        ("transferFee", c_double),
        # 印花税
        ("stampTax", c_double),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID，由客户在委托时提供
        ("orderID", c_uint32),
        # 批次ID，由客户在批量委托时提供，单个时与orderID相同
        ("batchID", c_uint32)
    ]


# 证券持仓
class STesStkPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账号（物理子账号，非虚拟子账号）
        ("subAccount", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
        # 组合合约代码
        ("comboSymbol", c_char * 33),
        # 持仓日期
        ("posDate", c_uint32),
        # 当前总持仓
        ("totalPos", c_int64),
        # 今仓数量(受今日买入 / 卖出 / 申购 / 赎回操作影响)
        ("todayPos", c_int64),
        # 开仓冻结数量
        ("frozenOpenPos", c_int64),
        # 开仓冻结金额
        ("frozenOpenAmount", c_double),
        # 平仓冻结数量
        ("frozenClosePos", c_int64),
        # 平仓冻结金额
        ("frozenCloseAmount", c_double),
        # 锁定仓位
        ("lockPos", c_int64),
        # 备兑仓位
        ("coverPos", c_int64),
        # 今日开仓数量
        ("openVolume", c_int64),
        # 今日开仓金额
        ("openAmount", c_double),
        # 今日平仓数量
        ("closeVolume", c_int64),
        # 今日平仓金额
        ("closeAmount", c_double),
        # 持仓成本
        ("posCost", c_double),
        # 开仓成本
        ("openCost", c_double),
        # 手续费
        ("commission", c_double),
        # 过户费
        ("transferFee", c_double),
        # 印花税
        ("stampTax", c_double),
        # ETF：已申购仓位，当日申购可卖出不可再赎回，卖出时优先卖出
        # 成分股：当日申购的数量
        ("purchasePos", c_int64),
        # 成分股：已赎回仓位，当日赎回可卖出不可再申购，卖出时优先卖出
        # ETF：当日赎回的数量
        ("redeemPos", c_int64)
    ]


# 证券批量委托（头部）
class STesStkEntrustBatch(Structure):
    _pack_ = 1
    _fields_ = [
        # 批量证券总数
        ("count", c_int32),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端批次号，客户端自行维护，clientID + batchID应保证唯一性，且不与其他orderID冲突
        ("batchID", c_uint32)
    ]


# 证券批量撤单
class STesStkCancelBatch(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端批次号，客户端自行维护，clientID + batchID应保证唯一性，且不与其他orderID冲突
        ("batchID", c_uint32)
    ]


# 证券撤单所有
class STesStkCancelAll(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
    ]


# 证券清仓 name 1
class STesStkClearAll(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端批次号，客户端自行维护，clientID + batchID应保证唯一性，且不与其他orderID冲突
        ("batchID", c_uint32)
    ]


# 证券清仓 name 2
class STesStkClearPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 客户端ID，请使用在登录响应中返回的clientID
        ("clientID", c_uint64),
        # 客户端批次号，客户端自行维护，clientID + batchID应保证唯一性，且不与其他orderID冲突
        ("batchID", c_uint32)
    ]


# 证券查询报单
class STesStkQueryOrder(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID或批次ID
        ("orderOrBatchID", c_uint32),
        # 合约代码
        ("comboSymbol", c_char * 33),
        # 报单状态
        ("orderStatus", c_char)
    ]


# 证券查询成交
class STesStkQueryTrade(Structure):
    _pack_ = 1
    _fields_ = [
        # 委托账号（虚拟交易账号）
        ("account", c_char * 33),
        # 报单引用
        ("orderRef", c_char * 35),
        # 客户端ID，客户端登录TES后获得的ID
        ("clientID", c_uint64),
        # 报单ID或批次ID
        ("orderOrBatchID", c_uint32),
        # 合约代码
        ("comboSymbol", c_char * 33),
    ]


# 证券查询持仓
class STesStkQueryPosition(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账户类型，仅对LTS有效，一般不填（设0）
        ("type", c_uint32),
        # 合约代码
        ("comboSymbol", c_char * 33),
    ]


# 证券查询合约
class STesStkQueryContract(Structure):
    _pack_ = 1
    _fields_ = [
        # 组合合约代码
        ("comboSymbol", c_char * 33),
        # 合约代码
        ("symbol", c_char * 33),
        # 交易所代码
        ("exchange", c_char * 9),
    ]


# 证券查询资金
class STesStkQueryCapital(Structure):
    _pack_ = 1
    _fields_ = [
        # 虚拟交易账号
        ("account", c_char * 33),
        # 子账户类型，仅对LTS有效，一般不填（设0）
        ("type", c_uint32),
    ]
