class Strategy:
    def __init__(self):
        self.buy_term = 30
        self.sell_term = 30

    def donchan(self, data, last_data):

        highest = max(i["high_price"] for i in last_data[(-1 * self.buy_term):])
        lowest = min(i["low_price"] for i in last_data[(-1 * self.sell_term):])

        # もし、一定期間の高値を現在の高値が超えたら買い
        if data["high_price"] > highest:
            return {"side": "BUY", "price": highest}

        # もし、一定期間の安値を現在の安値が下回ったら売り
        if data["low_price"] < lowest:
            return {"side": "SELL", "price": lowest}

        # 上記どちらも満たさない場合、何もしない
        return {"side": None, "price": 0}
