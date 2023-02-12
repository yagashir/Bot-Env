from datetime import datetime
import json
import requests


class Input:
    def __init__(self):
        self.time = 3600
        self.before = 0
        self.after = 0
        self.request_url = "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc"
        self.csv_path = "../../latest_data/1514764800-1670371200-price_1d.json"
        self.price = []

    # CryptowatchのAPIを使用する関数

    def get_price(self):

        # 取得したい年月日の選択
        params = {"period": self.time}
        if self.before != 0:
            params["before"] = self.before
        if self.after != 0:
            params["after"] = self.after

        response = requests.get(self.request_url, params)
        data = response.json()

    # OHLCデータ取得
        if data["result"][str(self.time)] is not None:
            for i in data["result"][str(self.time)]:
                if i[1] != 0 and i[2] != 0 and i[3] != 0 and i[4] != 0:
                    self.price.append({"close_time": i[0],
                                       "close_time_dt": datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
                                       "open_price": i[1],
                                       "high_price": i[2],
                                       "low_price": i[3],
                                       "close_price": i[4]})
            return self.price

        else:
            print("データが存在しません")
            return None

    # json形式のファイルから価格データを読み込む関数

    def get_price_from_file(self):

        # csvのパスが設定されているなら
        if self.csv_path is not None:
            file = open(self.csv_path, 'r', encoding='utf-8')
            price = json.load(file)
            return price
