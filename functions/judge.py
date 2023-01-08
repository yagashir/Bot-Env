class Judge:
    def __init__(self):
        pass


    #引数　order_info : 注文状況（未約定）
    #返り値　True : 未約定の注文が存在する False : 存在しない
    def isOrder(self, order_info):
        if order_info["exist"]:
            return True
        else:
            return False


    #引数　signal : 売買のシグナル（Buy or Sell）
    #返り値　True : 売る　False : 売らない
    def isBear(self, signal):
        if signal["side"] == "SELL":
            return True
        else:
            return False


    #引数　signal : 売買のシグナル（Buy or Sell）
    #返り値　True : 買う　False : 買わない
    def isBull(self, signal):
        if signal["side"] == "BUY":
            return True
        else:
            return False


    def check_order(self):
        
        # 注文状況を確認して通っていたら(今後実装) True
        return True


    #引数　lot : 注文ロット数
    #返り値　True : 最低ロット数を超えている　False : 超えていない
    def isLotEnough(self, lot):
        if lot > 0.01:
            return True
        else:
            return False


    #引数　position_info : ポジション（保有）状況
    #返り値　True : ポジションを持っていない　False : 持っている
    def isClose(self, position_info):
        if position_info["exist"] == False:
            return True
        else:
            False

    
    #引数　position_info : ポジション（保有）状況
    #返り値　True : 買いのポジションを持っている　False : 買いのポジションを持っていない
    def isBuyPosition(self, position_info):
        if position_info["side"] == "BUY" and position_info["exist"] == True:
            return True
        else:
            return False

        
    #引数　position_info : ポジション（保有）状況
    #返り値　True : 売りのポジションを持っている　False : 売りのポジションを持っていない
    def isSellPosition(self, position_records):
        if position_records["side"] == "SELL" and position_records["exist"] == True:
            return True
        else:
            return False


    #引数　data : 最新のOHLC,　stop_price : 損切りの価格
    #返り値　True : 買いのポジションで損切りを実施する　False : 損切りを実施しない
    def isBuyPosLossCut(self, data, stop_price):
        if data["low_price"] < stop_price:
            return True
        else:
            return False

    
    #引数　data : 最新のOHLC, stop_price : 損切りの価格
    #返り値　True : 売りのポジションで損切りを実施する False : 損切りを実施しない
    def isSellPosLossCut(self, data, stop_price):
        if data["high_price"] > stop_price:
            return True
        else:
            return False
