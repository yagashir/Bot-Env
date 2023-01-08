from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Output:
    def __init__(self):
        self.start_funds = 300000

    def intro(self, price):
        print("--------------------------")
        print("テスト期間：")
        print("開始時点：" + str(price[0]["close_time_dt"]))
        print("終了時点：" + str(price[-1]["close_time_dt"]))
        print(str(len(price)) + "件のローソク足データで検証")
        print("--------------------------")
    
    
    # バックテストの集計用の関数
    def backtest(self, backtest_log, trade_log):
        # 成績を記録した pandas DataFrame を作成
        records = pd.DataFrame({
            "Date": pd.to_datetime(backtest_log["date"]),
            "Profit": backtest_log["profit"],
            "Side": backtest_log["side"],
            "Rate": backtest_log["return"],
            "STOP": backtest_log["stop-count"],
            "Periods": backtest_log["holding-periods"],
            "Slippage": backtest_log["slippage"]
        })

        # 連敗回数をカウントする
        consecutive_defeats = []
        defeats = 0
        for p in backtest_log["profit"]:
            if p < 0:
                defeats += 1
            else:
                # 連敗の記録
                consecutive_defeats.append(defeats)
                defeats = 0

        # 総損益の列を追加する
        records["Gross"] = records["Profit"].cumsum()

        # 資産推移の列を追加
        records["Funds"] = records["Gross"] + self.start_funds

        # 最大ドローダウンの列を追加する
        records["Drawdown"] = records["Funds"].cummax().subtract(records["Funds"])
        records["DrawdownRate"] = round(records["Drawdown"] / records["Funds"].cummax() * 100, 1)

        # 買いエントリと売りエントリだけをそれぞれ抽出する
        buy_records = records[records["Side"].isin(["BUY"])]
        sell_records = records[records["Side"].isin(["SELL"])]

        # 月別のデータを集計する
        records["月別集計"] = pd.to_datetime(records["Date"].apply(lambda x: x.strftime("%Y/%m")))
        grouped = records.groupby("月別集計")

        # 月別の成績
        month_records = pd.DataFrame({
            "Number": grouped["Profit"].count(),
            "Gross": grouped["Gross"].sum(),
            "Funds": grouped["Funds"].last(),
            "Rate": round(grouped["Rate"].mean(), 2),
            "Drawdown": grouped["Drawdown"].max(),
            "Periods": grouped["Periods"].mean()
        })

        print("バックテストの結果")
        print("--------------------------")
        print("買いエントリの成績")
        print("--------------------------")
        print("トレード回数　： {}回".format(len(buy_records)))
        print("勝率　　　　　： {}％".format(round(len(buy_records[buy_records["Profit"] > 0]) / len(buy_records) * 100, 1)))
        print("平均リターン　： {}％".format(round(buy_records["Rate"].mean(), 2)))
        print("総利益　　　　： {}円".format(buy_records["Profit"].sum()))
        print("平均保有期間　： {}足分".format(round(buy_records["Periods"]).mean(), 1))
        print("損切の回数　　： {}回".format(buy_records["STOP"].sum()))

        print("--------------------------")
        print("売りエントリの成績")
        print("--------------------------")
        print("トレード回数　： {}回".format(len(sell_records)))
        print("勝率　　　　　： {}％".format(round(len(sell_records[sell_records["Profit"] > 0]) / len(sell_records) * 100, 1)))
        print("平均リターン　： {}％".format(round(sell_records["Rate"].mean(), 2)))
        print("総利益　　　　： {}円".format(sell_records["Profit"].sum()))
        print("平均保有期間　： {}足分".format(round(sell_records["Periods"]).mean(), 1))
        print("損切の回数　　： {}回".format(round(sell_records["STOP"].sum())))

        print("--------------------------")
        print("総合の成績")
        print("--------------------------")
        print("全トレード数　　　： {}回".format(len(records)))
        print("勝率　　　　　　　： {}％".format(round(len(records[records["Profit"] > 0]) / len(records) * 100, 1)))
        print("平均リターン　　　： {}％".format(round(records["Rate"].mean(), 2)))
        print("平均保有期間　　　： {}足分".format(round(records["Periods"].mean(), 1)))
        print("損切の回数　　　　： {}回".format(records["STOP"].sum()))
        print("")
        print("最大の勝ちトレード： {}円".format(records["Profit"].max()))
        print("最大の負けトレード： {}円".format(records["Profit"].min()))
        print("最大連敗回数　　　： {}回".format(max(consecutive_defeats)))
        print("最大ドローダウン　： {0}円 / {1}%".format(-1 * records["Drawdown"].max(), -1 * records["DrawdownRate"].loc[records["Drawdown"].idxmax()]))
        print("利益合計　　　　　： {}円".format(records[records["Profit"] > 0]["Profit"].sum()))
        print("損益合計　　　　　： {}円".format(records[records["Profit"] < 0]["Profit"].sum()))
        print("最終損益　　　　　： {}円".format(records["Profit"].sum()))
        print("")
        print("初期資金　　　　　： {}円".format(self.start_funds))
        print("最終資金　　　　　： {}円".format(records["Funds"].iloc[-1]))
        print("運用成績　　　　　： {}％".format(round(records["Funds"].iloc[-1] / self.start_funds * 100, 2)))
        print("手数料合計　　　　： {}円".format(-1 * records["Slippage"].sum()))

        print("------------------------------")
        print("月別の成績")

        for index, row in month_records.iterrows():
            print("--------------------------")
            print("{0}年{1}月の成績".format(index.year, index.month))
            print("--------------------------")
            print("トレード数　　　： {}回".format(row["Number"].astype(int)))
            print("月間損益　　　　： {}円".format(row["Gross"].astype(int)))
            print("平均リターン　　： {}％".format(row["Rate"]))
            print("月間ドローダウン： {}円".format(-1 * row["Drawdown"].astype(int)))
            print("月末資金　　　　： {}円".format(row["Funds"].astype(int)))

        file = open("./{0}-donchian-log.txt".format(
            datetime.now().strftime("%Y-%m-%d-%H-%M")), "wt", encoding="utf-8")
        file.writelines(trade_log)

        # 損益曲線をプロット
        plt.plot(records["Date"], records["Funds"])
        plt.xlabel("Date")
        plt.ylabel("Balance")
        plt.xticks(rotation=50)  # X軸の目盛りを 50 度回転

        plt.show()

