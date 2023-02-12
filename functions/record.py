import numpy as np
from datetime import datetime


class Record:
    def __init__(self):
        pass


    #未約定の注文が存在しないという状態に更新　
    def order_pass(self, order_info):
        order_info["exist"] = False
        order_info["count"] = 0
        return order_info


    #引数　order_info : 注文状況、position_info : ポジション状況
    #返り値　ポジションの獲得
    def get_position(self, order_info, position_info):
        position_info["exist"] = True
        position_info["side"] = order_info["side"]
        position_info["stop"] = order_info["stop"]
        position_info["price"] = order_info["price"]
        position_info["lot"] = order_info["lot"]
        return position_info


    #ポジションの保有期間の記録
    def keep_count(self, position_info):
        position_info["count"] += 1
        return position_info

    def add_position_count(self, add_position_info):
        add_position_info["count"] += 1
        return add_position_info


    #ポジション状況の更新
    def close_position(self, position_info):
        position_info["exist"] = False
        position_info["count"] = 0
        return position_info


    #引数　lot : ロット数、stop : 損切り価格、data : 最新のOHLC
    #買いの注文状況の更新
    def get_buy_order(self, lot, stop, data, order_info):
        order_info["exist"] = True
        order_info["lot"] = lot
        order_info["stop"] = stop
        order_info["side"] = "BUY"
        order_info["price"] = data["close_price"]
        return order_info


    #引数　lot : ロット数、stop : 損切り価格、data : 最新のOHLC
    #売りの注文状況の更新
    def get_sell_order(self, lot, stop, data, order_info):
        order_info["exist"] = True
        order_info["lot"] = lot
        order_info["stop"] = stop
        order_info["side"] = "SELL"
        order_info["price"] = data["close_price"]
        return order_info

    def first_entry(self, position_info, add_position_info):
        add_position_info["first-entry-price"] = position_info["price"]
        add_position_info["last-entry-price"] = position_info["price"]
        add_position_info["count"] += 1
        return add_position_info


    def first_add_position_update(self, unit_size, unit_range, stop, add_position_info):
        add_position_info["unit-size"] = unit_size
        add_position_info["unit-range"] = unit_range
        add_position_info["stop"] = stop
        return add_position_info


    def add_position_update(self, stop, entry_price, lot, position_info, add_position_info):
        position_info["stop"] = stop
        position_info["price"] = int(round((position_info["price"] * position_info["lot"] + entry_price * lot) / (position_info["lot"] + lot)))
        position_info["lot"] = np.round((position_info["lot"] + lot) * 100) / 100
        add_position_info["count"] += 1
        add_position_info["last_entry_price"] = entry_price
        return position_info, add_position_info

