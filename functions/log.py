from datetime import datetime


class Log:
    def __init__(self):
        self.slippage = 0.01
        self.buy_term = 30
        self.sell_term = 30


    def price(self, data, trade_log):
        log = "時間： " + datetime.fromtimestamp(data["close_time"]).strftime(
            '%Y/%m/%d %H:%M') + " 高値： " + str(data["high_price"]) + " 安値： " + str(data["low_price"]) + "\n"
        trade_log.append(log)
        return trade_log


    def loss_cut(self, real_stop_price, trade_log):
        trade_log.append("{0}円の損切ラインに引っかかりました。\n".format(real_stop_price))
        return trade_log


    def lot(self, calc_lot, able_lot, trade_log, backtest_log):
        trade_log.append("現在のアカウント残高は{}円です\n".format(backtest_log["funds"]))
        trade_log.append(
            "許容リスクから購入できる枚数は最大{}BTCまでです\n".format(calc_lot))
        trade_log.append(
            "証拠金から購入できる枚数は最大{}BTCまでです\n".format(able_lot))
        return trade_log


    def buy_breakout(self, signal, data, trade_log):
        trade_log.append("過去{0}足の最高値{1}円を、直近の高値が{2}円でブレイクしました\n".format(
            self.buy_term, signal["price"], data["high_price"]))
        return trade_log


    def sell_breakout(self, signal, data, trade_log):
        trade_log.append("過去{0}足の最安値{1}円を、直近の安値が{2}円でブレイクしました\n".format(
            self.sell_term, signal["price"], data["low_price"]))
        return trade_log



    def buy_limit(self, data, trade_log):
        trade_log.append(str(data["close_price"]) + "円で買いの指値注文を出します\n")
        return trade_log


    def sell_limit(self, data, trade_log):
        trade_log.append(str(data["close_price"]) + "円で売りの指値注文を出します\n")
        return trade_log


    def close_buy_position(self, trade_log):
        trade_log.append("成行注文を出して「買い」のポジションを決済します\n")
        return trade_log


    def close_sell_position(self, trade_log):
        trade_log.append("成行注文を出して「売り」のポジションを決済します\n")
        return trade_log


    def buy_stop_line(self, stop, data, trade_log):
        trade_log.append("{0}円にストップを入れます\n".format(data["close_price"] - stop))
        return trade_log


    def sell_stop_line(self, stop, data, trade_log):
        trade_log.append("{0}円にストップを入れます\n".format(data["close_price"] + stop))
        return trade_log


    def slippage_cost(self, trade_cost, trade_log):
        trade_log.append("スリッページ・手数料として" + str(trade_cost) + "円を考慮します\n")
        return trade_log


    def buy_position_profit(self, buy_position_profit, trade_log):
        if buy_position_profit > 0:
            trade_log.append(str(abs(buy_position_profit)) + "円の利益です\n")
            return trade_log
        else:
            trade_log.append(str(abs(buy_position_profit)) + "円の損失です\n")
            return trade_log


    def sell_position_profit(self, sell_position_profit, trade_log):
        if sell_position_profit > 0:
            trade_log.append(str(abs(sell_position_profit)) + "円の利益です\n")
            return trade_log
        else:
            trade_log.append(str(abs(sell_position_profit)) + "円の損失です\n")
            return trade_log


    def buy_position_close_records(self, entry_price, trade_cost, buy_position_profit, data, position_info, backtest_log, close_type=None):
        # 手仕舞った日時と保有期間の記録
        backtest_log["date"].append(data["close_time_dt"])
        backtest_log["holding-periods"].append(position_info["count"])

        #取引手数料の計算
        backtest_log["slippage"].append(trade_cost)

        # 損切にかかった回数をカウント
        if close_type == "STOP":
            backtest_log["stop-count"].append(1)
        else:
            backtest_log["stop-count"].append(0)

        # 利益の記録
        backtest_log["side"].append("BUY")
        backtest_log["profit"].append(buy_position_profit)
        backtest_log["return"].append(round(buy_position_profit / entry_price * 100, 4))
        backtest_log["funds"] += buy_position_profit

        return backtest_log


    # 各トレードのパフォーマンスを記録する関数
    def sell_position_close_records(self, entry_price, trade_cost, sell_position_profit, data, position_info, backtest_log, close_type=None):

        # 手仕舞った日時と保有期間の記録
        backtest_log["date"].append(data["close_time_dt"])
        backtest_log["holding-periods"].append(position_info["count"])

        # 取引手数料の記録
        backtest_log["slippage"].append(trade_cost)

        # 損切にかかった回数をカウント
        if close_type == "STOP":
            backtest_log["stop-count"].append(1)
        else:
            backtest_log["stop-count"].append(0)

        # 利益の記録
        backtest_log["side"].append("SELL")
        backtest_log["profit"].append(sell_position_profit)
        backtest_log["return"].append(round(sell_position_profit / entry_price * 100, 4))
        backtest_log["funds"] += sell_position_profit

        return backtest_log
