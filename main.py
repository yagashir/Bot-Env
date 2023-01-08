import requests
from datetime import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json


from functions import calculate
from functions import input
from functions import judge
from functions import log
from functions import order
from functions import output
from functions import record


from Strategies import donchan


# 設定ファイルの読み込み
f = open("configuration/config.json", "r", encoding="utf-8")
config = json.load(f)
config["need_term"] = max(config["buy_term"], config["sell_term"], config["volatility_term"])


order_info = {
    "exist": False,
    "side": "",
    "price": 0,
    "stop": 0,
    "ATR": 0,
    "lot": 0,
    "count": 0
}

position_info = {
    "exist": False,
    "side": "",
    "price": 0,
    "stop": 0,
    "ATR": 0,
    "lot": 0,
    "count": 0
}

backtest_log = {
    "date": [],
    "profit": [],
    "return": [],
    "side": [],
    "stop-count": [],
    "holding-periods": [],
    "drawdown": 0,
    "slippage": [],
    "funds": config["start_funds"]
}

trade_log = []


# 入力インスタンス生成
input = input.Input()

# 入力の初期設定
input.time = config["chart_sec"]
input.before = config["get_time_before"]
input.after = config["get_time_after"]
input.request_url = config["request_url"]
input.csv_path = config["csv_path"]


# 売買ロジックのインスタンス生成
strategy = donchan.Strategy()

#売買ロジックの初期設定
strategy.buy_term = config["buy_term"]
strategy.sell_term = config["sell_term"]


# その他インスタンス生成（注文、シグナル生成、etc）
calculate = calculate.Calculate()
judge = judge.Judge()
log = log.Log()
record = record.Record()

# その他初期設定
calculate.chart_sec = config["chart_sec"]
calculate.volatility_term = config["volatility_term"]
calculate.stop_range = config["stop_range"]
calculate.trade_risk = config["trade_risk"]
calculate.leverage = config["leverage"]
calculate.slippage = config["slippage"]
log.buy_term = config["buy_term"]
log.sell_term = config["sell_term"]
log.slippage = config["slippage"]


# 出力インスタンス生成
output = output.Output()
# 出力の初期設定
output.start_funds = config["start_funds"]

# ------メインループ------------------------------------------

# チャートを取得
# APIを叩いてチャート取得するなら
# price = Input.get_price()
price = input.get_price_from_file()

last_data = []
i = 0
while i < len(price):

    # 過去の一定期間の価格を取得
    while len(last_data) < config["need_term"]:
        last_data.append(price[i])
        trade_log = log.price(price[i], trade_log)
        time.sleep(config["wait"])
        i += 1
        continue

    # 現在のOHLC取得、flagの更新
    data = price[i]
    trade_log = log.price(data, trade_log)

    # 未約定の注文があるなら
    if judge.isOrder(order_info):
        if judge.check_order():
            order_info = record.order_pass(order_info)
            position_info = record.get_position(order_info, position_info)

    #買いのポジションを持っているなら
    elif judge.isBuyPosition(position_info):
        #損切り
        stop_price = calculate.buy_stop_price(position_info)

        if judge.isBuyPosLossCut(data, stop_price):
            real_stop_price = calculate.buy_real_stop_price(stop_price, last_data)

            #成行で決済

            #処理
            entry_price, exit_price = calculate.entry_exit_price(data["close_price"], position_info)
            trade_cost = calculate.cost(exit_price)

            #ログ
            trade_log = log.loss_cut(real_stop_price, trade_log)
            trade_log = log.close_buy_position(trade_log)
            trade_log = log.slippage_cost(trade_cost, trade_log)
            trade_log = log.profit(entry_price, exit_price, trade_cost, trade_log)

            #バックテスト・ポジションの記録
            backtest_log = log.records(entry_price, exit_price, trade_cost, data, position_info, backtest_log, close_type="STOP")
            position_info = record.close_position(position_info)

        #損切りを既にしていたら
        if judge.isClose(position_info):
            pass
        else:
            position_info = record.keep_count(position_info)

            signal = strategy.donchan(data, last_data)
            if judge.isBear(signal):

                #成行で決済

                #処理
                entry_price, exit_price = calculate.entry_exit_price(data["close_price"], position_info)
                trade_cost = calculate.cost(exit_price)
                #ドテンを行うためにロットを計算
                stop = calculate.stop(last_data)
                lot, calc_lot, able_lot = calculate.lot(last_data, data, backtest_log)

                #ログ
                trade_log = log.sell_breakout(signal, data, trade_log)
                trade_log = log.close_buy_position(trade_log)
                trade_log = log.slippage_cost(trade_cost, trade_log)
                trade_log = log.profit(entry_price, exit_price, trade_cost, trade_log)
                trade_log = log.lot(calc_lot, able_lot, trade_log, backtest_log)

                #バックテスト・ポジションの記録
                backtest_log = log.records(entry_price, exit_price, trade_cost, data, position_info, backtest_log, close_type=None)
                position_info = record.close_position(position_info)
                

                if judge.isLotEnough(lot):

                    #ドテン注文

                    #オーダーの記録
                    order_info = record.get_sell_order(lot, stop, data, order_info)

                    #ログ系
                    trade_log = log.sell_limit(data, trade_log)
                    trade_log = log.sell_stop_line(stop, data, trade_log)
                    
                else:
                    print("注文可能枚数{}が、最低注文単位に満たなかったので注文を見送ります".format(lot))


    #売りのポジションを持っているなら
    elif judge.isSellPosition(position_info):
        #損切り
        stop_price = calculate.sell_stop_price(position_info)
        if judge.isSellPosLossCut(data, stop_price):
            real_stop_price = calculate.sell_real_stop_price(stop_price, last_data)

            #成行で決済

            #処理
            entry_price, exit_price = calculate.entry_exit_price(data["close_price"], position_info)
            trade_cost = calculate.cost(exit_price)
            
            #ログ
            trade_log = log.loss_cut(real_stop_price, trade_log)
            trade_log = log.close_sell_position(trade_log)
            trade_log = log.slippage_cost(trade_cost, trade_log)
            trade_log = log.profit(entry_price, exit_price, trade_cost, trade_log)

            #バックテスト・ポジションの記録
            backtest_log = log.records(entry_price, exit_price, trade_cost, data, position_info, backtest_log, close_type="STOP")
            position_info = record.close_position(position_info)

        #損切りを既にしていたら
        if judge.isClose(position_info):
            pass
        else:
            position_info = record.keep_count(position_info)
            
            signal = strategy.donchan(data, last_data)

            if judge.isBull(signal):

                #成行で決済

                #処理
                entry_price, exit_price = calculate.entry_exit_price(data["close_price"], position_info)
                trade_cost = calculate.cost(exit_price)
                #ドテンを行うためにロットを計算
                stop = calculate.stop(last_data)
                lot, calc_lot, able_lot = calculate.lot(last_data, data, backtest_log)
                
                #ログ
                trade_log = log.buy_breakout(signal, data, trade_log)
                trade_log = log.close_sell_position(trade_log)
                trade_log = log.slippage_cost(trade_cost, trade_log)
                trade_log = log.profit(entry_price, exit_price, trade_cost, trade_log)
                trade_log = log.lot(calc_lot, able_lot, trade_log, backtest_log)

                #バックテスト・ポジションの記録
                backtest_log = log.records(entry_price, exit_price, trade_cost, data, position_info, backtest_log, close_type=None)
                position_info = record.close_position(position_info)
                

                if judge.isLotEnough(lot):

                    #ドテン注文

                    #オーダーの記録
                    order_info = record.get_buy_order(lot, stop, data, order_info)
                    
                    #ログ
                    trade_log = log.buy_limit(data, trade_log)
                    trade_log = log.buy_stop_line(stop, data, trade_log)

                else:
                    print("注文可能枚数{}が、最低注文単位に満たなかったので注文を見送ります".format(lot))

    else:
        signal = strategy.donchan(data, last_data)

        if judge.isBull(signal):
            #処理
            stop = calculate.stop(last_data)
            lot, calc_lot, able_lot = calculate.lot(last_data, data, backtest_log)

            #ログ
            trade_log = log.buy_breakout(signal, data, trade_log)
            trade_log = log.lot(calc_lot, able_lot, trade_log, backtest_log)

            if judge.isLotEnough(lot):

                #買い注文

                #オーダーの記録
                order_info = record.get_buy_order(lot, stop, data, order_info)
                
                #ログ
                trade_log = log.buy_limit(data, trade_log)
                trade_log = log.buy_stop_line(stop, data, trade_log)

            else:
                print("注文可能枚数{}が、最低注文単位に満たなかったので注文を見送ります".format(lot))


        if judge.isBear(signal):
            #処理
            stop = calculate.stop(last_data)
            lot, calc_lot, able_lot = calculate.lot(last_data, data, backtest_log)

            #ログ
            trade_log = log.sell_breakout(signal, data, trade_log)
            trade_log = log.lot(calc_lot, able_lot, trade_log, backtest_log)
            
            if judge.isLotEnough(lot):

                #売り注文

                #オーダーの記録
                order_info = record.get_sell_order(lot, stop, data, order_info)
                
                #ログ
                trade_log = log.sell_limit(data, trade_log)
                trade_log = log.sell_stop_line(stop, data, trade_log)

                
            else:
                print("注文可能枚数{}が、最低注文単位に満たなかったので注文を見送ります".format(lot))



    # 過去の一定期間の価格を更新
    last_data.append(data)

    i += 1
    time.sleep(config["wait"])


# 出力----------------------------------------------------------------------------

output.intro(price)
output.backtest(backtest_log, trade_log)
