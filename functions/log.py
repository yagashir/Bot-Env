from datetime import datetime


class Log:
    def __init__(self):
        self.slippage = 0.01
        self.buy_term = 30
        self.sell_term = 30
        self.entry_times = 2


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
        trade_log.append("許容リスクから購入できる枚数は最大{}BTCまでです\n".format(calc_lot))
        trade_log.append("証拠金から購入できる枚数は最大{}BTCまでです\n".format(able_lot))
        return trade_log


    def first_lot(self, calc_lot, entry_times, unit_size, trade_log, backtest_log):
        trade_log.append("現在のアカウント残高は{}円です\n".format(backtest_log["funds"]))
        trade_log.append("許容リスクから購入できる枚数は最大{}BTCまでです\n".format(calc_lot))
        trade_log.append("{0}回に分けて{1}BTCずつ注文します".format(entry_times, unit_size))
        return trade_log


    def pass_lot(self, lot, trade_log):
        trade_log.append("注文可能枚数{}が、最低注文単位に満たなかったので注文を見送ります\n".format(lot))
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


    def buy_stop_line(self, stop, price, trade_log):
        trade_log.append("{0}円にストップを入れます\n".format(price - stop))
        return trade_log


    def sell_stop_line(self, stop, price, trade_log):
        trade_log.append("{0}円にストップを入れます\n".format(price + stop))
        return trade_log


    def slippage_cost(self, trade_cost, trade_log):
        trade_log.append("スリッページ・手数料として" + str(trade_cost) + "円を考慮します\n")
        return trade_log


    def profit(self, profit, trade_log):
        if profit > 0:
            trade_log.append(str(abs(profit)) + "円の利益です\n")
        else:
            trade_log.append(str(abs(profit)) + "円の損失です\n")

        return trade_log


    # 各トレードのパフォーマンスを記録する関数
    def position_closing(self, current_position, entry_price, trade_cost, profit, data, position_info, backtest_log, close_type=None):
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
        backtest_log["side"].append(current_position)
        backtest_log["profit"].append(profit)
        backtest_log["return"].append(round(profit / entry_price * 100, 4))
        backtest_log["funds"] += profit

        return backtest_log


    def move_unit_range(self, last_entry_price, unit_range, add_position_info, trade_log):
        trade_log.append("\n前回のエントリー価格{0}円からブレイクアウトの方向に{1}ATR（{2}円）以上動きました\n".format(last_entry_price, entry_range, round(unit_range)))
        trade_log.append("{0}/{1}回目の追加注文を出します\n".format(add_position_info["count"] + 1, self.entry_times))
        return trade_log


    def current_position_information(self, position_info, trade_log):
        trade_log.append("現在のポジションの取得単価は{}円です\n".format(position_info["price"]))
        trade_log.append("現在のポジションサイズは{}BTCです\n\n".format(position_info["lot"]))
        return trade_log

