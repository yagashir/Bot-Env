import numpy as np


class Calculate:
    def __init__(self):
        self.chart_sec = 60
        self.volatility_term = 30
        self.stop_range = 2
        self.trade_risk = 0.001
        self.leverage = 3
        self.slippage = 0.01
        self.entry_times = 2
        self.entry_range = 0.5


    def volatility(self, last_data):
        high_sum = sum(i["high_price"] for i in last_data[(-1 * self.volatility_term):])
        low_sum = sum(i["low_price"] for i in last_data[(-1 * self.volatility_term):])
        volatility = round((high_sum - low_sum) / self.volatility_term)
        return volatility


    def stop(self, last_data):
        volatility = self.volatility(last_data)
        stop = self.stop_range * volatility
        return stop


    def balance(self, position_info, backtest_log):
        balance = backtest_log["funds"]
        balance = round(balance - position_info["price"] * position_info["lot"] / self.leverage)
        return balance


    def first_lot_etc(self, balance, last_data, backtest_log):
        volatility = self.volatility(last_data)
        stop = self.stop_range * volatility
        calc_lot = np.floor(balance * self.trade_risk / stop * 100) / 100
        unit_size = np.floor(calc_lot / self.entry_times * 100) / 100
        unit_range = round(volatility * self.entry_range)
        return calc_lot, unit_size, unit_range, stop, self.entry_times


    def lot(self, balance, last_data, data, add_position_info, backtest_log):
        # 1期間のボラティリティを基準にストップ位置を計算する
        stop = add_position_info["stop"]

        # 注文可能なロット数を計算する
        able_lot = np.floor(balance * self.leverage / data["close_price"] * 100) / 100
        lot = min(able_lot, add_position_info["unit-size"])
        return lot, able_lot, stop


    def added_entry_price(self, first_entry_price, unit_range, add_position_info):
        entry_price = first_entry_price + (add_position_info["count"] * unit_range)
        entry_price = (1 + self.slippage) * entry_price
        return entry_price


    def buy_stop_price(self, position_info):
        stop_price = position_info["price"] - position_info["stop"]
        return stop_price


    def buy_real_stop_price(self, stop_price, last_data):
        real_stop_price = round(stop_price - 2 * Calculate.volatility(self, last_data) / (self.chart_sec / 60))
        return real_stop_price


    def sell_stop_price(self, position_info):
        stop_price = position_info["price"] + position_info["stop"]
        return stop_price


    def sell_real_stop_price(self, stop_price, last_data):
        real_stop_price = round(stop_price + 2 * Calculate.volatility(self, last_data) / (self.chart_sec / 60))
        return real_stop_price


    def trade_cost(self, close_price, position_info):
        exit_price = int(round(close_price * position_info["lot"]))
        trade_cost = round(exit_price * self.slippage)
        return trade_cost


    def entry_exit_price(self, close_price, position_info):
        entry_price = int(round(position_info["price"] * position_info["lot"]))
        exit_price = int(round(close_price * position_info["lot"]))
        return entry_price, exit_price


    def buy_position_profit(self, entry_price, exit_price, trade_cost):
        buy_position_profit = exit_price - entry_price - trade_cost
        return buy_position_profit

    def sell_position_profit(self, entry_price, exit_price, trade_cost):
        sell_position_profit = entry_price - exit_price - trade_cost
        return sell_position_profit

    def cost(self, exit_price):
        trade_cost = round(exit_price * self.slippage)
        return trade_cost



