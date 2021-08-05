from trade_api.c_struct import *

"""
opt_trade_wrapper callback
"""
opt_on_connected = CFUNCTYPE(None, c_void_p)
opt_on_disconnected = CFUNCTYPE(None, c_void_p, POINTER(STesError))
opt_on_rsp_login = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogin), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_logout = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogout), POINTER(STesError), c_uint32, c_bool)
opt_on_ready = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
opt_on_req_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
opt_on_rsp_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
opt_on_rsp_entrust_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptEntrustOrder), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_cancel_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptCancelOrder), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_capital = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptCapital), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_contract = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptContract), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptOrder), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_trade = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptTrade), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_position = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptPosition), POINTER(STesError), c_uint32, c_bool)
opt_on_rsp_query_quote = CFUNCTYPE(None, c_void_p, POINTER(
    STesOptQuoteData), POINTER(STesError), c_uint32, c_bool)
opt_on_rtn_error = CFUNCTYPE(None, c_void_p, POINTER(STesError))
opt_on_rtn_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptOrder))
opt_on_rtn_trade = CFUNCTYPE(None, c_void_p, POINTER(STesOptTrade))
opt_on_position_change = CFUNCTYPE(None, c_void_p, POINTER(STesOptPosition))
opt_on_contract_status_change = CFUNCTYPE(
    c_void_p, POINTER(STesOptContractStatusChange))
# 备兑行权
opt_on_rsp_covered_lock = CFUNCTYPE(None, c_void_p, POINTER(STesOptLockRequest), POINTER(STesError),
                                    c_uint32,
                                    c_bool)
opt_on_rsp_query_lock_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptLockOrder), POINTER(STesError),
                                        c_uint32,
                                        c_bool)
opt_on_rsp_query_lock_position = CFUNCTYPE(None, c_void_p, POINTER(STesOptLockPosition),
                                           POINTER(STesError),
                                           c_uint32, c_bool)
opt_on_rtn_lock = CFUNCTYPE(None, c_void_p, POINTER(STesOptLockOrder))
opt_on_lock_position_change = CFUNCTYPE(None, c_void_p, POINTER(STesOptLockPosition))
opt_on_rsp_entrust_exec_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptEntrustExecOrder),
                                          POINTER(STesError),
                                          c_uint32, c_bool)
opt_on_rsp_cancel_exec_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptCancelExecOrder),
                                         POINTER(STesError),
                                         c_uint32, c_bool)
opt_on_rsp_query_exec_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptExecOrder), POINTER(STesError),
                                        c_uint32,
                                        c_bool)
opt_on_rtn_exec_order = CFUNCTYPE(None, c_void_p, POINTER(STesOptExecOrder))


def redefine_opt_trade_wrapper_func(opt_trade_wrapper_dll: CDLL) -> CDLL:
    """CTesTradeConfig 对象及方法包装"""
    # 创建配置对象
    opt_trade_wrapper_dll.opt_config_create.argtypes = []
    opt_trade_wrapper_dll.opt_config_create.restype = c_void_p

    # 销毁配置对象
    opt_trade_wrapper_dll.opt_config_destroy.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_destroy.restype = c_void_p

    # 设置配置属性-账号
    opt_trade_wrapper_dll.opt_config_set_account.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_account.restype = c_void_p

    # 设置配置属性-名称
    opt_trade_wrapper_dll.opt_config_set_name.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_name.restype = c_void_p

    # 设置配置属性-驱动
    opt_trade_wrapper_dll.opt_config_set_driver.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_driver.restype = c_void_p

    # 设置配置属性-版本
    opt_trade_wrapper_dll.opt_config_set_version.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_version.restype = c_void_p

    # 设置配置属性-库文件路径
    opt_trade_wrapper_dll.opt_config_set_lib_path.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_lib_path.restype = c_void_p

    # 设置配置属性-日志路径
    opt_trade_wrapper_dll.opt_config_set_log_path.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_log_path.restype = c_void_p

    # 设置配置属性-通用方法
    opt_trade_wrapper_dll.opt_config_set_attribute.argtypes = [
        c_void_p, c_char_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_set_attribute.restype = c_void_p

    # 获取配置属性-账号
    opt_trade_wrapper_dll.opt_config_get_account.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_account.restype = c_char_p

    # 获取配置属性-名称
    opt_trade_wrapper_dll.opt_config_get_name.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_name.restype = c_char_p

    # 获取配置属性-驱动
    opt_trade_wrapper_dll.opt_config_get_driver.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_driver.restype = c_char_p

    # 获取配置属性-版本
    opt_trade_wrapper_dll.opt_config_get_version.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_version.restype = c_char_p

    # 获取配置属性-库文件路径
    opt_trade_wrapper_dll.opt_config_get_lib_path.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_lib_path.restype = c_char_p

    # 获取配置属性-日志路径
    opt_trade_wrapper_dll.opt_config_get_log_path.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_config_get_log_path.restype = c_char_p

    # 获取配置属性-通用方法
    opt_trade_wrapper_dll.opt_config_get_attribute.argtypes = [c_void_p, c_char_p]
    opt_trade_wrapper_dll.opt_config_get_attribute.restype = c_char_p

    """CTesOptTradeProxy 对象及方法包装"""
    # 创建对象
    opt_trade_wrapper_dll.opt_api_create.argtypes = [c_void_p, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_create.restype = c_void_p

    # 销毁对象
    opt_trade_wrapper_dll.opt_api_destroy.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_api_destroy.restype = c_void_p

    # 设置回调-OnConnected
    opt_trade_wrapper_dll.opt_api_set_cb_connected.argtypes = [
        c_void_p, opt_on_connected]
    opt_trade_wrapper_dll.opt_api_set_cb_connected.restype = c_void_p

    # 设置回调 - OnDisconnected
    opt_trade_wrapper_dll.opt_api_set_cb_disconnected.argtypes = [
        c_void_p, opt_on_disconnected]
    opt_trade_wrapper_dll.opt_api_set_cb_disconnected.restype = c_void_p

    # 设置回调 - OnRspLogin
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_login.argtypes = [
        c_void_p, opt_on_rsp_login]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_login.restype = c_void_p

    # 设置回调 - OnRspLogout
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_logout.argtypes = [
        c_void_p, opt_on_rsp_logout]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_logout.restype = c_void_p

    # 设置回调 - OnReady
    opt_trade_wrapper_dll.opt_api_set_cb_ready.argtypes = [c_void_p, opt_on_ready]
    opt_trade_wrapper_dll.opt_api_set_cb_ready.restype = c_void_p

    # 设置回调-OnReqError
    opt_trade_wrapper_dll.opt_api_set_cb_req_error.argtypes = [
        c_void_p, opt_on_req_error]
    opt_trade_wrapper_dll.opt_api_set_cb_req_error.restype = c_void_p

    # 设置回调 - OnRspError
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_error.argtypes = [
        c_void_p, opt_on_rsp_error]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_error.restype = c_void_p

    # 设置回调 - OnRspEntrustOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_entrust_order.argtypes = [
        c_void_p, opt_on_rsp_entrust_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_entrust_order.restype = c_void_p

    # 设置回调 - OnRspCancelOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_cancel_order.argtypes = [
        c_void_p, opt_on_rsp_cancel_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_cancel_order.restype = c_void_p

    # 设置回调 - OnRspQueryCapital
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_capital.argtypes = [
        c_void_p, opt_on_rsp_query_capital]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_capital.restype = c_void_p

    # 设置回调 - OnRspQueryContract
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_contract.argtypes = [
        c_void_p, opt_on_rsp_query_contract]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_contract.restype = c_void_p

    # 设置回调 - OnRspQueryOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_order.argtypes = [
        c_void_p, opt_on_rsp_query_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_order.restype = c_void_p

    # 设置回调-OnRspQueryTrade
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_trade.argtypes = [
        c_void_p, opt_on_rsp_query_trade]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_trade.restype = c_void_p

    # 设置回调 - OnRspQueryPosition
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_position.argtypes = [
        c_void_p, opt_on_rsp_query_position]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_position.restype = c_void_p

    # 设置回调 - OnRspQueryQuote
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_quote.argtypes = [
        c_void_p, opt_on_rsp_query_quote]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_quote.restype = c_void_p

    # 设置回调 - OnRtnError
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_error.argtypes = [
        c_void_p, opt_on_rtn_error]
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_error.restype = c_void_p

    # 设置回调 - OnRtnOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_order.argtypes = [
        c_void_p, opt_on_rtn_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_order.restype = c_void_p

    # 设置回调 - OnRtnTrade
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_trade.argtypes = [
        c_void_p, opt_on_rtn_trade]
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_trade.restype = c_void_p

    # 设置回调-OnPositionChange
    opt_trade_wrapper_dll.opt_api_set_cb_position_change.argtypes = [
        c_void_p, opt_on_position_change]
    opt_trade_wrapper_dll.opt_api_set_cb_position_change.restype = c_void_p

    # 设置回调 - OnContractStatusChange
    opt_trade_wrapper_dll.opt_api_set_cb_contract_status_change.argtypes = [
        c_void_p, opt_on_contract_status_change]
    opt_trade_wrapper_dll.opt_api_set_cb_contract_status_change.restype = c_void_p

    # 初始化
    opt_trade_wrapper_dll.opt_api_initialize.argtypes = [c_void_p, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_initialize.restype = c_void_p

    # 是否完成初始化
    opt_trade_wrapper_dll.opt_api_is_initialized.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_api_is_initialized.restype = c_bool

    # 终止
    opt_trade_wrapper_dll.opt_api_finalize.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_api_finalize.restype = c_void_p

    # 登录账号
    opt_trade_wrapper_dll.opt_api_login.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_login.restype = c_void_p

    # 是否完成登录
    opt_trade_wrapper_dll.opt_api_is_logined.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_api_is_logined.restype = c_bool

    # 登出账号
    opt_trade_wrapper_dll.opt_api_logout.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_logout.restype = c_void_p

    # 是否完成准备
    opt_trade_wrapper_dll.opt_api_is_ready.argtypes = [c_void_p]
    opt_trade_wrapper_dll.opt_api_is_ready.restype = c_bool

    # 委托
    opt_trade_wrapper_dll.opt_api_entrust.argtypes = [c_void_p, POINTER(
        STesOptEntrustOrder), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_entrust.restype = c_void_p

    # 撤单
    opt_trade_wrapper_dll.opt_api_cancel.argtypes = [c_void_p, POINTER(
        STesOptCancelOrder), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_cancel.restype = c_void_p

    # 订单查询
    opt_trade_wrapper_dll.opt_api_query_orders.argtypes = [c_void_p, POINTER(STesOptQueryOrder), c_uint32,
                                                           POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_orders.restype = c_void_p

    # 成交查询
    opt_trade_wrapper_dll.opt_api_query_trades.argtypes = [
        c_void_p, POINTER(STesOptQueryTrade), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_trades.restype = c_void_p

    # 持仓查询
    opt_trade_wrapper_dll.opt_api_query_positions.argtypes = [
        c_void_p, POINTER(STesOptQueryPosition), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_positions.restype = c_void_p

    # 合约查询
    opt_trade_wrapper_dll.opt_api_query_contracts.argtypes = [
        c_void_p, POINTER(STesOptQueryContract), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_contracts.restype = c_void_p

    # 行情查询
    opt_trade_wrapper_dll.opt_api_query_quote.argtypes = [c_void_p, POINTER(
        STesOptQueryQuote), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_quote.restype = c_void_p

    # 账户资金查询
    opt_trade_wrapper_dll.opt_api_query_capital.argtypes = [
        c_void_p, POINTER(STesOptQueryCapital), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_capital.restype = c_void_p

    # 提交终端信息
    opt_trade_wrapper_dll.opt_api_submit_system_info.argtypes = [
        c_void_p, POINTER(STesUserSystemInfo), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_submit_system_info.restype = c_void_p

    # 注册终端信息
    opt_trade_wrapper_dll.opt_api_register_system_info.argtypes = [
        c_void_p, POINTER(STesUserSystemInfo), c_uint32, POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_register_system_info.restype = c_void_p

    """备兑，行权相关"""
    # 锁定 / 解锁证券（仅限股票期权备兑业务）
    opt_trade_wrapper_dll.opt_api_covered_lock.argtypes = [c_void_p, POINTER(STesOptLockRequest), c_uint32,
                                                           POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_covered_lock.restype = c_void_p

    # 查询备兑锁定委托
    opt_trade_wrapper_dll.opt_api_query_lock_orders.argtypes = [c_void_p, POINTER(STesOptQueryLockOrder), c_uint32,
                                                                POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_lock_orders.restype = c_void_p

    # 查询备兑证券持仓
    opt_trade_wrapper_dll.opt_api_query_lock_positions.argtypes = [c_void_p, POINTER(STesOptQueryLockPosition),
                                                                   c_uint32,
                                                                   POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_lock_positions.restype = c_void_p

    # 期权行权委托
    opt_trade_wrapper_dll.opt_api_entrust_exercise.argtypes = [c_void_p, POINTER(STesOptEntrustExecOrder), c_uint32,
                                                               POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_entrust_exercise.restype = c_void_p

    # 期权撤销行权
    opt_trade_wrapper_dll.opt_api_cancel_exercise.argtypes = [c_void_p, POINTER(STesOptCancelExecOrder), c_uint32,
                                                              POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_cancel_exercise.restype = c_void_p

    # 查询行权委托
    opt_trade_wrapper_dll.opt_api_query_exec_orders.argtypes = [c_void_p, POINTER(STesOptQueryExecOrder), c_uint32,
                                                                POINTER(STesError)]
    opt_trade_wrapper_dll.opt_api_query_exec_orders.restype = c_void_p

    # 设置回调-OnRspCoveredLock
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_covered_lock.argtypes = [c_void_p, opt_on_rsp_covered_lock]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_covered_lock.restype = c_void_p

    # 设置回调-OnRspQueryLockOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_lock_order.argtypes = [c_void_p, opt_on_rsp_query_lock_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_lock_order.restype = c_void_p

    # 设置回调-OnRspQueryLockPosition
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_lock_position.argtypes = [c_void_p, opt_on_rsp_query_lock_position]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_lock_position.restype = c_void_p

    # 设置回调-OnRtnLock
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_lock.argtypes = [c_void_p, opt_on_rtn_lock]
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_lock.restype = c_void_p

    # 设置回调-OnLockPositionChange
    opt_trade_wrapper_dll.opt_api_set_cb_lock_position_change.argtypes = [c_void_p, opt_on_lock_position_change]
    opt_trade_wrapper_dll.opt_api_set_cb_lock_position_change.restype = c_void_p

    # 设置回调-OnRspEntrustExecOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_entrust_exec_order.argtypes = [c_void_p, opt_on_rsp_entrust_exec_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_entrust_exec_order.restype = c_void_p

    # 设置回调-OnRspCancelExecOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_cancel_exec_order.argtypes = [c_void_p, opt_on_rsp_cancel_exec_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_cancel_exec_order.restype = c_void_p

    # 设置回调-OnRspQueryExecOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_exec_order.argtypes = [c_void_p, opt_on_rsp_query_exec_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rsp_query_exec_order.restype = c_void_p

    # 设置回调-OnRtnExecOrder
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_exec_order.argtypes = [c_void_p, opt_on_rtn_exec_order]
    opt_trade_wrapper_dll.opt_api_set_cb_rtn_exec_order.restype = c_void_p

    return opt_trade_wrapper_dll


"""
ftr_trade_wrapper callback
"""
ftr_on_connected = CFUNCTYPE(None, c_void_p)
ftr_on_disconnected = CFUNCTYPE(None, c_void_p, POINTER(STesError))
ftr_on_rsp_login = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogin), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_logout = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogout), POINTER(STesError), c_uint32, c_bool)
ftr_on_ready = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
ftr_on_req_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
ftr_on_rsp_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
ftr_on_rsp_entrust_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrEntrustOrder), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_cancel_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrCancelOrder), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_query_capital = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrCapital), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_query_contract = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrContract), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_query_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrOrder), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_query_trade = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrTrade), POINTER(STesError), c_uint32, c_bool)
ftr_on_rsp_query_position = CFUNCTYPE(None, c_void_p, POINTER(
    STesFtrPosition), POINTER(STesError), c_uint32, c_bool)
ftr_on_rtn_error = CFUNCTYPE(None, c_void_p, POINTER(STesError))
ftr_on_rtn_order = CFUNCTYPE(None, c_void_p, POINTER(STesFtrOrder))
ftr_on_rtn_trade = CFUNCTYPE(None, c_void_p, POINTER(STesFtrTrade))
ftr_on_position_change = CFUNCTYPE(None, c_void_p, POINTER(STesFtrPosition))


def redefine_ftr_trade_wrapper_func(ftr_trade_wrapper_dll: CDLL) -> CDLL:
    # 创建配置对象
    ftr_trade_wrapper_dll.ftr_config_create.argtypes = []
    ftr_trade_wrapper_dll.ftr_config_create.restype = c_void_p

    # 销毁配置对象
    ftr_trade_wrapper_dll.ftr_config_destroy.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_destroy.restype = c_void_p

    # 设置配置属性-账号
    ftr_trade_wrapper_dll.ftr_config_set_account.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_account.restype = c_void_p

    # 设置配置属性-名称
    ftr_trade_wrapper_dll.ftr_config_set_name.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_name.restype = c_void_p

    # 设置配置属性-驱动
    ftr_trade_wrapper_dll.ftr_config_set_driver.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_driver.restype = c_void_p

    # 设置配置属性-版本
    ftr_trade_wrapper_dll.ftr_config_set_version.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_version.restype = c_void_p

    # 设置配置属性-库文件路径
    ftr_trade_wrapper_dll.ftr_config_set_lib_path.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_lib_path.restype = c_void_p

    # 设置配置属性-日志路径
    ftr_trade_wrapper_dll.ftr_config_set_log_path.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_log_path.restype = c_void_p

    # 设置配置属性-通用方法
    ftr_trade_wrapper_dll.ftr_config_set_attribute.argtypes = [
        c_void_p, c_char_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_set_attribute.restype = c_void_p

    # 获取配置属性-账号
    ftr_trade_wrapper_dll.ftr_config_get_account.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_account.restype = c_char_p

    # 获取配置属性-名称
    ftr_trade_wrapper_dll.ftr_config_get_name.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_name.restype = c_char_p

    # 获取配置属性-驱动
    ftr_trade_wrapper_dll.ftr_config_get_driver.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_driver.restype = c_char_p

    # 获取配置属性-版本
    ftr_trade_wrapper_dll.ftr_config_get_version.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_version.restype = c_char_p

    # 获取配置属性-库文件路径
    ftr_trade_wrapper_dll.ftr_config_get_lib_path.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_lib_path.restype = c_char_p

    # 获取配置属性-日志路径
    ftr_trade_wrapper_dll.ftr_config_get_log_path.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_config_get_log_path.restype = c_char_p

    # 获取配置属性-通用方法
    ftr_trade_wrapper_dll.ftr_config_get_attribute.argtypes = [c_void_p, c_char_p]
    ftr_trade_wrapper_dll.ftr_config_get_attribute.restype = c_char_p

    """CTesFtrTradeProxy 对象及方法包装"""
    # 创建对象
    ftr_trade_wrapper_dll.ftr_api_create.argtypes = [c_void_p, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_create.restype = c_void_p

    # 销毁对象
    ftr_trade_wrapper_dll.ftr_api_destroy.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_api_destroy.restype = c_void_p

    # 设置回调-OnConnected
    ftr_trade_wrapper_dll.ftr_api_set_cb_connected.argtypes = [
        c_void_p, ftr_on_connected]
    ftr_trade_wrapper_dll.ftr_api_set_cb_connected.restype = c_void_p

    # 设置回调 - OnDisconnected
    ftr_trade_wrapper_dll.ftr_api_set_cb_disconnected.argtypes = [
        c_void_p, ftr_on_disconnected]
    ftr_trade_wrapper_dll.ftr_api_set_cb_disconnected.restype = c_void_p

    # 设置回调 - OnRspLogin
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_login.argtypes = [
        c_void_p, ftr_on_rsp_login]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_login.restype = c_void_p

    # 设置回调 - OnRspLogout
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_logout.argtypes = [
        c_void_p, ftr_on_rsp_logout]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_logout.restype = c_void_p

    # 设置回调 - OnReady
    ftr_trade_wrapper_dll.ftr_api_set_cb_ready.argtypes = [c_void_p, ftr_on_ready]
    ftr_trade_wrapper_dll.ftr_api_set_cb_ready.restype = c_void_p

    # 设置回调-OnReqError
    ftr_trade_wrapper_dll.ftr_api_set_cb_req_error.argtypes = [
        c_void_p, ftr_on_req_error]
    ftr_trade_wrapper_dll.ftr_api_set_cb_req_error.restype = c_void_p

    # 设置回调 - OnRspError
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_error.argtypes = [
        c_void_p, ftr_on_rsp_error]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_error.restype = c_void_p

    # 设置回调 - OnRspEntrustOrder
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_entrust_order.argtypes = [
        c_void_p, ftr_on_rsp_entrust_order]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_entrust_order.restype = c_void_p

    # 设置回调 - OnRspCancelOrder
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_cancel_order.argtypes = [
        c_void_p, ftr_on_rsp_cancel_order]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_cancel_order.restype = c_void_p

    # 设置回调 - OnRspQueryCapital
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_capital.argtypes = [
        c_void_p, ftr_on_rsp_query_capital]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_capital.restype = c_void_p

    # 设置回调 - OnRspQueryContract
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_contract.argtypes = [
        c_void_p, ftr_on_rsp_query_contract]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_contract.restype = c_void_p

    # 设置回调 - OnRspQueryOrder
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_order.argtypes = [
        c_void_p, ftr_on_rsp_query_order]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_order.restype = c_void_p

    # 设置回调-OnRspQueryTrade
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_trade.argtypes = [
        c_void_p, ftr_on_rsp_query_trade]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_trade.restype = c_void_p

    # 设置回调 - OnRspQueryPosition
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_position.argtypes = [
        c_void_p, ftr_on_rsp_query_position]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rsp_query_position.restype = c_void_p

    # 设置回调 - OnRtnError
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_error.argtypes = [
        c_void_p, ftr_on_rtn_error]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_error.restype = c_void_p

    # 设置回调 - OnRtnOrder
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_order.argtypes = [
        c_void_p, ftr_on_rtn_order]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_order.restype = c_void_p

    # 设置回调 - OnRtnTrade
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_trade.argtypes = [
        c_void_p, ftr_on_rtn_trade]
    ftr_trade_wrapper_dll.ftr_api_set_cb_rtn_trade.restype = c_void_p

    # 设置回调-OnPositionChange
    ftr_trade_wrapper_dll.ftr_api_set_cb_position_change.argtypes = [
        c_void_p, ftr_on_position_change]
    ftr_trade_wrapper_dll.ftr_api_set_cb_position_change.restype = c_void_p

    # 初始化
    ftr_trade_wrapper_dll.ftr_api_initialize.argtypes = [c_void_p, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_initialize.restype = c_void_p

    # 是否完成初始化
    ftr_trade_wrapper_dll.ftr_api_is_initialized.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_api_is_initialized.restype = c_bool

    # 终止
    ftr_trade_wrapper_dll.ftr_api_finalize.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_api_finalize.restype = c_void_p

    # 登录账号
    ftr_trade_wrapper_dll.ftr_api_login.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_login.restype = c_void_p

    # 是否完成登录
    ftr_trade_wrapper_dll.ftr_api_is_logined.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_api_is_logined.restype = c_bool

    # 登出账号
    ftr_trade_wrapper_dll.ftr_api_logout.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_logout.restype = c_void_p

    # 是否完成准备
    ftr_trade_wrapper_dll.ftr_api_is_ready.argtypes = [c_void_p]
    ftr_trade_wrapper_dll.ftr_api_is_ready.restype = c_bool

    # 委托
    ftr_trade_wrapper_dll.ftr_api_entrust.argtypes = [c_void_p, POINTER(
        STesFtrEntrustOrder), c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_entrust.restype = c_void_p

    # 撤单
    ftr_trade_wrapper_dll.ftr_api_cancel.argtypes = [c_void_p, POINTER(
        STesFtrCancelOrder), c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_cancel.restype = c_void_p

    # 委托查询
    ftr_trade_wrapper_dll.ftr_api_query_orders.argtypes = [c_void_p, POINTER(
        STesFtrQueryOrder), c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_query_orders.restype = c_void_p

    # 成交查询
    ftr_trade_wrapper_dll.ftr_api_query_trades.argtypes = [c_void_p, POINTER(
        STesFtrQueryTrade), c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_query_trades.restype = c_void_p

    # 持仓查询
    ftr_trade_wrapper_dll.ftr_api_query_positions.argtypes = [c_void_p, POINTER(STesFtrQueryPosition), c_uint32,
                                                 POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_query_positions.restype = c_void_p

    # 合约查询
    ftr_trade_wrapper_dll.ftr_api_query_contracts.argtypes = [c_void_p, POINTER(STesFtrQueryContract), c_uint32,
                                                 POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_query_contracts.restype = c_void_p

    # 账户资金查询
    ftr_trade_wrapper_dll.ftr_api_query_capital.argtypes = [c_void_p, POINTER(
        STesFtrQueryCapital), c_uint32, POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_query_capital.restype = c_void_p

    # 提交终端信息
    ftr_trade_wrapper_dll.ftr_api_submit_system_info.argtypes = [c_void_p, POINTER(STesUserSystemInfo), c_uint32,
                                                    POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_submit_system_info.restype = c_void_p

    # 注册终端信息
    ftr_trade_wrapper_dll.ftr_api_register_system_info.argtypes = [c_void_p, POINTER(STesUserSystemInfo), c_uint32,
                                                      POINTER(STesError)]
    ftr_trade_wrapper_dll.ftr_api_register_system_info.restype = c_void_p
    
    return ftr_trade_wrapper_dll


"""
stk_trade_wrapper callback
"""
stk_on_connected = CFUNCTYPE(None, c_void_p)
stk_on_disconnected = CFUNCTYPE(None, c_void_p, POINTER(STesError))
stk_on_rsp_login = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogin), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_logout = CFUNCTYPE(None, c_void_p, POINTER(
    STesRspLogout), POINTER(STesError), c_uint32, c_bool)
stk_on_ready = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
stk_on_req_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
stk_on_rsp_error = CFUNCTYPE(None, c_void_p, POINTER(STesError), c_uint32)
stk_on_rsp_entrust_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkEntrustOrder), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_cancel_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkCancelOrder), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_query_capital = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkCapital), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_query_contract = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkContract), POINTER(STesError), c_uint32, c_bool)

stk_on_rsp_query_etf_contract = CFUNCTYPE(None, c_void_p, POINTER(STesStkEtfContract), POINTER(STesError),
                                               c_uint32,
                                               c_bool)
stk_on_rsp_query_etf_component = CFUNCTYPE(None, c_void_p, POINTER(STesStkEtfComponent),
                                                POINTER(STesError),
                                                c_uint32,
                                                c_bool)

stk_on_rsp_query_order = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkOrder), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_query_trade = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkTrade), POINTER(STesError), c_uint32, c_bool)
stk_on_rsp_query_position = CFUNCTYPE(None, c_void_p, POINTER(
    STesStkPosition), POINTER(STesError), c_uint32, c_bool)
stk_on_rtn_error = CFUNCTYPE(None, c_void_p, POINTER(STesError))
stk_on_rtn_order = CFUNCTYPE(None, c_void_p, POINTER(STesStkOrder))
stk_on_rtn_trade = CFUNCTYPE(None, c_void_p, POINTER(STesStkTrade))
stk_on_position_change = CFUNCTYPE(None, c_void_p, POINTER(STesStkPosition))

def redefine_stk_trade_wrapper_func(stk_trade_wrapper_dll: CDLL) -> CDLL:
    # 创建配置对象
    stk_trade_wrapper_dll.stk_config_create.argtypes = []
    stk_trade_wrapper_dll.stk_config_create.restype = c_void_p

    # 销毁配置对象
    stk_trade_wrapper_dll.stk_config_destroy.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_destroy.restype = c_void_p

    # 设置配置属性-账号
    stk_trade_wrapper_dll.stk_config_set_account.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_account.restype = c_void_p

    # 设置配置属性-名称
    stk_trade_wrapper_dll.stk_config_set_name.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_name.restype = c_void_p

    # 设置配置属性-驱动
    stk_trade_wrapper_dll.stk_config_set_driver.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_driver.restype = c_void_p

    # 设置配置属性-版本
    stk_trade_wrapper_dll.stk_config_set_version.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_version.restype = c_void_p

    # 设置配置属性-库文件路径
    stk_trade_wrapper_dll.stk_config_set_lib_path.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_lib_path.restype = c_void_p

    # 设置配置属性-日志路径
    stk_trade_wrapper_dll.stk_config_set_log_path.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_log_path.restype = c_void_p

    # 设置配置属性-通用方法
    stk_trade_wrapper_dll.stk_config_set_attribute.argtypes = [
        c_void_p, c_char_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_set_attribute.restype = c_void_p

    # 获取配置属性-账号
    stk_trade_wrapper_dll.stk_config_get_account.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_account.restype = c_char_p

    # 获取配置属性-名称
    stk_trade_wrapper_dll.stk_config_get_name.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_name.restype = c_char_p

    # 获取配置属性-驱动
    stk_trade_wrapper_dll.stk_config_get_driver.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_driver.restype = c_char_p

    # 获取配置属性-版本
    stk_trade_wrapper_dll.stk_config_get_version.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_version.restype = c_char_p

    # 获取配置属性-库文件路径
    stk_trade_wrapper_dll.stk_config_get_lib_path.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_lib_path.restype = c_char_p

    # 获取配置属性-日志路径
    stk_trade_wrapper_dll.stk_config_get_log_path.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_config_get_log_path.restype = c_char_p

    # 获取配置属性-通用方法
    stk_trade_wrapper_dll.stk_config_get_attribute.argtypes = [c_void_p, c_char_p]
    stk_trade_wrapper_dll.stk_config_get_attribute.restype = c_char_p

    """CTesStkTradeProxy 对象及方法包装"""
    # 创建对象
    stk_trade_wrapper_dll.stk_api_create.argtypes = [c_void_p, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_create.restype = c_void_p

    # 销毁对象
    stk_trade_wrapper_dll.stk_api_destroy.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_api_destroy.restype = c_void_p

    # 设置回调-OnConnected
    stk_trade_wrapper_dll.stk_api_set_cb_connected.argtypes = [
        c_void_p, stk_on_connected]
    stk_trade_wrapper_dll.stk_api_set_cb_connected.restype = c_void_p

    # 设置回调 - OnDisconnected
    stk_trade_wrapper_dll.stk_api_set_cb_disconnected.argtypes = [
        c_void_p, stk_on_disconnected]
    stk_trade_wrapper_dll.stk_api_set_cb_disconnected.restype = c_void_p

    # 设置回调 - OnRspLogin
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_login.argtypes = [
        c_void_p, stk_on_rsp_login]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_login.restype = c_void_p

    # 设置回调 - OnRspLogout
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_logout.argtypes = [
        c_void_p, stk_on_rsp_logout]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_logout.restype = c_void_p

    # 设置回调 - OnReady
    stk_trade_wrapper_dll.stk_api_set_cb_ready.argtypes = [c_void_p, stk_on_ready]
    stk_trade_wrapper_dll.stk_api_set_cb_ready.restype = c_void_p

    # 设置回调-OnReqError
    stk_trade_wrapper_dll.stk_api_set_cb_req_error.argtypes = [
        c_void_p, stk_on_req_error]
    stk_trade_wrapper_dll.stk_api_set_cb_req_error.restype = c_void_p

    # 设置回调 - OnRspError
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_error.argtypes = [
        c_void_p, stk_on_rsp_error]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_error.restype = c_void_p

    # 设置回调 - OnRspEntrustOrder
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_entrust_order.argtypes = [
        c_void_p, stk_on_rsp_entrust_order]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_entrust_order.restype = c_void_p

    # 设置回调 - OnRspCancelOrder
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_cancel_order.argtypes = [
        c_void_p, stk_on_rsp_cancel_order]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_cancel_order.restype = c_void_p

    # 设置回调 - OnRspQueryCapital
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_capital.argtypes = [
        c_void_p, stk_on_rsp_query_capital]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_capital.restype = c_void_p

    # 设置回调 - OnRspQueryContract
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_contract.argtypes = [
        c_void_p, stk_on_rsp_query_contract]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_contract.restype = c_void_p

    # 设置回调 - OnRspQueryEtfContract
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_etf_contract.argtypes = [
        c_void_p, stk_on_rsp_query_etf_contract]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_etf_contract.restype = c_void_p

    # 设置回调 - OnRspQueryEtfComponent
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_etf_component.argtypes = [
        c_void_p, stk_on_rsp_query_etf_component]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_etf_component.restype = c_void_p

    # 设置回调 - OnRspQueryOrder
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_order.argtypes = [
        c_void_p, stk_on_rsp_query_order]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_order.restype = c_void_p

    # 设置回调-OnRspQueryTrade
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_trade.argtypes = [
        c_void_p, stk_on_rsp_query_trade]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_trade.restype = c_void_p

    # 设置回调 - OnRspQueryPosition
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_position.argtypes = [
        c_void_p, stk_on_rsp_query_position]
    stk_trade_wrapper_dll.stk_api_set_cb_rsp_query_position.restype = c_void_p

    # 设置回调 - OnRtnError
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_error.argtypes = [
        c_void_p, stk_on_rtn_error]
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_error.restype = c_void_p

    # 设置回调 - OnRtnOrder
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_order.argtypes = [
        c_void_p, stk_on_rtn_order]
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_order.restype = c_void_p

    # 设置回调 - OnRtnTrade
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_trade.argtypes = [
        c_void_p, stk_on_rtn_trade]
    stk_trade_wrapper_dll.stk_api_set_cb_rtn_trade.restype = c_void_p

    # 设置回调-OnPositionChange
    stk_trade_wrapper_dll.stk_api_set_cb_position_change.argtypes = [
        c_void_p, stk_on_position_change]
    stk_trade_wrapper_dll.stk_api_set_cb_position_change.restype = c_void_p

    # 初始化
    stk_trade_wrapper_dll.stk_api_initialize.argtypes = [c_void_p, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_initialize.restype = c_void_p

    # 是否完成初始化
    stk_trade_wrapper_dll.stk_api_is_initialized.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_api_is_initialized.restype = c_bool

    # 终止
    stk_trade_wrapper_dll.stk_api_finalize.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_api_finalize.restype = c_void_p

    # 登录账号
    stk_trade_wrapper_dll.stk_api_login.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_login.restype = c_void_p

    # 是否完成登录
    stk_trade_wrapper_dll.stk_api_is_logined.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_api_is_logined.restype = c_bool

    # 登出账号
    stk_trade_wrapper_dll.stk_api_logout.argtypes = [
        c_void_p, c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_logout.restype = c_void_p

    # 是否完成准备
    stk_trade_wrapper_dll.stk_api_is_ready.argtypes = [c_void_p]
    stk_trade_wrapper_dll.stk_api_is_ready.restype = c_bool

    # 委托
    stk_trade_wrapper_dll.stk_api_entrust.argtypes = [c_void_p, POINTER(
        STesStkEntrustOrder), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_entrust.restype = c_void_p

    # 批量委托
    stk_trade_wrapper_dll.stk_api_batch_entrust.argtypes = [c_void_p, POINTER(STesStkEntrustBatch), POINTER(STesStkEntrustOrder),
                                               c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_batch_entrust.restype = c_void_p

    # 撤单
    stk_trade_wrapper_dll.stk_api_cancel.argtypes = [c_void_p, POINTER(
        STesStkCancelOrder), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_cancel.restype = c_void_p

    # 批量撤单
    stk_trade_wrapper_dll.stk_api_batch_cancel.argtypes = [c_void_p, POINTER(
        STesStkCancelBatch), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_batch_cancel.restype = c_void_p

    # 撤所有可撤单
    stk_trade_wrapper_dll.stk_api_cancel_all.argtypes = [c_void_p, POINTER(STesStkCancelAll), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_cancel_all.restype = c_void_p

    # 清仓（卖出所有可卖）
    stk_trade_wrapper_dll.stk_api_clear_all.argtypes = [c_void_p, POINTER(STesStkClearAll), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_clear_all.restype = c_void_p

    # 订单查询
    stk_trade_wrapper_dll.stk_api_query_orders.argtypes = [c_void_p, POINTER(STesStkQueryOrder), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_query_orders.restype = c_void_p

    # 成交查询
    stk_trade_wrapper_dll.stk_api_query_trades.argtypes = [c_void_p, POINTER(STesStkQueryTrade), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_query_trades.restype = c_void_p

    # 持仓查询
    stk_trade_wrapper_dll.stk_api_query_positions.argtypes = [c_void_p, POINTER(STesStkQueryPosition), c_uint32,
                                                 POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_query_positions.restype = c_void_p

    # 账户资金查询
    stk_trade_wrapper_dll.stk_api_query_capital.argtypes = [c_void_p, POINTER(STesStkQueryCapital), c_uint32, POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_query_capital.restype = c_void_p

    # 合约查询
    stk_trade_wrapper_dll.stk_api_query_contracts.argtypes = [c_void_p, POINTER(STesStkQueryContract), c_uint32,
                                                 POINTER(STesError)]
    stk_trade_wrapper_dll.stk_api_query_contracts.restype = c_void_p
    
    return stk_trade_wrapper_dll