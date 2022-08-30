import os

import sys

import numpy as np
import pandas as pd

import backtrader as bt
from datetime import datetime

AUD_MID_PATH = r"datas/AUD_USD/MID/AUD_USD_MID.csv"
EUR_MID_PATH = r"datas/EUR_USD/MID/EUR_USD_MID.csv"
GBP_MID_PATH = r"datas/GBP_USD/MID/GBP_USD_MID.csv"


class MyStrategy(bt.Strategy):
    params = (
        ('eur_stoploss', 3000),
        ('eur_takeprofit', 3000),
        ('eur_open_count', 10),
        ('eur_close_count', 5),
        ('aud_stoploss', 3000),
        ('aud_takeprofit', 3000),
        ('aud_open_count', 10),
        ('aud_close_count', 5),
        ('gbp_stoploss', 3000),
        ('gbp_takeprofit', 3000),
        ('gbp_open_count', 10),
        ('gbp_close_count', 5),
    )

    def __init__(self):

        self.counter = -1
        self.order = None
        self.eur = self.datas[0]
        self.aud = self.datas[2]
        self.gbp = self.datas[1]

        self.close_eur = self.datas[0].close
        self.close_aud = self.datas[2].close
        self.close_gbp = self.datas[1].close

        self.eur_pos = None
        self.aud_pos = None
        self.gbp_pos = None

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])

        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED on {order.data._name}, Price: %.5f, Size: %.2f, Position = %.2f' %
                    (
                        order.executed.price,
                        order.executed.size,
                        self.getposition(order.data).size
                    )
                )
            else:
                # Sell
                self.log(
                    f'SELL EXECUTED on {order.data._name}, Price: %.5f, Size: %.2f, Position = %.2f' %
                    (
                        order.executed.price,
                        order.executed.size,
                        self.getposition(order.data).size
                    )
                )
        elif order.status in [order.Canceled]:
            self.log(
                f'{order.price} ON  {order.data._name} Order Canceleds ')

        self.order = None

    def get_eur_limitprice(self, close_price):
        profit_per_one = self.p.eur_takeprofit / 300000
        return close_price + profit_per_one

    def get_eur_stopprice(self, close_price):
        loss_per_one = self.p.eur_stoploss / 300000
        return close_price + loss_per_one

    def get_aud_limitprice(self, close_price):
        profit_per_one = self.p.aud_takeprofit / 300000
        return close_price + profit_per_one

    def get_aud_stopprice(self, close_price):
        loss_per_one = self.p.aud_stoploss / 300000
        return close_price + loss_per_one

    def get_gbp_limitprice(self, close_price):
        profit_per_one = self.p.gbp_takeprofit / 300000
        return close_price + profit_per_one

    def get_gbp_stopprice(self, close_price):
        loss_per_one = self.p.gbp_stoploss / 300000
        return close_price + loss_per_one

    def next(self):

        self.counter += 1
        if self.counter < 10:
            return


# -----------------------------------------------------------EUR/USD-----------------------------------------------
        check_open_count_eur = np.diff(self.close_eur.get(ago=0, size=10))
        check_close_count_eur = np.diff(self.close_eur.get(ago=0, size=5))
        self.eur_pos = self.getposition(self.eur).size

        if np.all(check_open_count_eur > 0) and (not self.eur_pos):
            self.eur_bracket_buy = self.buy_bracket(data=self.eur, size=300000,
                                                    price=self.close_eur[0],
                                                    limitprice=self.get_eur_limitprice(
                                                        self.close_eur[0]),
                                                    stopprice=self.get_eur_stopprice(
                                                        self.close_eur[0])
                                                    )
            self.log(
                f"BUY on  pos = {self.eur_pos} On EUR/USD, %.5f" % self.close_eur[0])
        elif np.all(check_close_count_eur > 0) and self.eur_pos < 0:
            if self.eur_bracket_sell:
                self.cancel(self.eur_bracket_sell[1])
                self.cancel(self.eur_bracket_sell[2])
            self.close(data=self.eur)
            self.log(
                f"CLOSE  pos = {self.eur_pos} On EUR/USD, %.5f" % self.close_eur[0])
        if np.all(check_open_count_eur < 0) and (not self.eur_pos):
            self.eur_bracket_sell = self.sell_bracket(data=self.eur, size=-300000,
                                                      price=self.close_eur[0],
                                                      stopprice=self.get_eur_limitprice(
                                                          self.close_eur[0]),
                                                      limitprice=self.get_eur_stopprice(
                                                          self.close_eur[0])
                                                      )
            self.log(
                f"SELL on  pos = {self.eur_pos} On EUR/USD, %.5f" % self.close_eur[0])
        elif np.all(check_close_count_eur > 0) and self.eur_pos > 0:
            if self.eur_bracket_buy:
                self.cancel(self.eur_bracket_buy[1])
                self.cancel(self.eur_bracket_buy[2])
            self.close(data=self.eur)
            self.log(
                f"CLOSE  pos = {self.eur_pos} On EUR/USD, %.5f" % self.close_eur[0])


# ----------------------------------------------------------GBP/USD--------------------------------------------------------
        check_open_count_gbp = np.diff(self.close_gbp.get(ago=0, size=10))
        check_close_count_gbp = np.diff(self.close_gbp.get(ago=0, size=5))
        self.gbp_pos = self.getposition(self.gbp).size

        if np.all(check_open_count_gbp < 0) and (not self.gbp_pos):
            self.gbp_bracket_sell = self.sell_bracket(data=self.gbp, size=-300000,
                                                      price=self.close_gbp[0],
                                                      stopprice=self.get_gbp_limitprice(
                                                          self.close_gbp[0]),
                                                      limitprice=self.get_gbp_stopprice(
                                                          self.close_gbp[0])
                                                      )
            self.log(
                f"SELL on  pos = {self.gbp_pos} On GBP/USD, %.5f" % self.close_gbp[0])
        elif np.all(check_close_count_gbp > 0) and self.gbp_pos > 0:
            if self.gbp_bracket_buy:
                self.cancel(self.gbp_bracket_buy[1])
                self.cancel(self.gbp_bracket_buy[2])
            self.close(data=self.gbp)
            self.log(
                f"CLOSE  pos = {self.gbp_pos} On GBP/USD, %.5f" % self.close_gbp[0])
        elif np.all(check_open_count_gbp > 0) and (not self.gbp_pos):
            self.gbp_bracket_buy = self.buy_bracket(data=self.gbp, size=300000,
                                                    price=self.close_gbp[0],
                                                    limitprice=self.get_gbp_limitprice(
                                                        self.close_gbp[0]),
                                                    stopprice=self.get_gbp_stopprice(
                                                        self.close_gbp[0])
                                                    )
            self.log(
                f"BUY on  pos = {self.gbp_pos} On GBP/USD, %.5f" % self.close_gbp[0])
        elif np.all(check_close_count_gbp > 0) and self.gbp_pos < 0:
            if self.gbp_bracket_sell:
                self.cancel(self.gbp_bracket_sell[1])
                self.cancel(self.gbp_bracket_sell[2])
            self.close(data=self.gbp)
            self.log(
                f"CLOSE  pos = {self.gbp_pos} On GBP/USD, %.5f" % self.close_[0])

# ----------------------------------------------------------AUD/USD--------------------------------------------------------
        check_open_count_aud = np.diff(self.close_aud.get(ago=0, size=10))
        check_close_count_aud = np.diff(self.close_aud.get(ago=0, size=5))
        self.aud_pos = self.getposition(self.aud).size

        if np.all(check_open_count_aud < 0) and (not self.aud_pos):
            self.aud_bracket_sell = self.sell_bracket(data=self.aud, size=-300000,
                                                      price=self.close_aud[0],
                                                      stopprice=self.get_aud_limitprice(
                                                          self.close_aud[0]),
                                                      limitprice=self.get_aud_stopprice(
                                                          self.close_aud[0])
                                                      )
            self.log(
                f"SELL on  pos = {self.aud_pos} On EUR/USD, %.5f" % self.close_aud[0])
        elif np.all(check_close_count_aud < 0) and self.aud_pos > 0:
            if self.aud_bracket_buy:
                self.cancel(self.aud_bracket_buy[1])
                self.cancel(self.aud_bracket_buy[2])
            self.close(data=self.aud)
            self.log(
                f"CLOSE  pos = {self.aud_pos} On AUD/USD, %.5f" % self.close_aud[0])
        elif np.all(check_open_count_aud > 0) and (not self.aud_pos):
            self.aud_bracket_buy = self.buy_bracket(data=self.aud, size=300000,
                                                    price=self.close_aud[0],
                                                    limitprice=self.get_aud_limitprice(
                                                        self.close_aud[0]),
                                                    stopprice=self.get_aud_stopprice(
                                                        self.close_aud[0])
                                                    )
            self.log(
                f"BUY on  pos = {self.aud_pos} On AUD/USD, %.5f" % self.close_aud[0])
        elif np.all(check_close_count_aud > 0) and self.aud_pos < 0:
            if self.aud_bracket_sell:
                self.cancel(self.aud_bracket_sell[1])
                self.cancel(self.aud_bracket_sell[2])
            self.close(data=self.aud)
            self.log(
                f"CLOSE  pos = {self.aud_pos} On AUD/USD, %.5f" % self.close_aud[0])


def start():

    cb = bt.Cerebro()

    cb.broker.set_cash(1000000)

    print("Cerebro created")

    aud_df = pd.read_csv(AUD_MID_PATH, index_col=0, parse_dates=True)
    # print(aud_df.head())
    aud_data = bt.feeds.PandasDirectData(

        dataname=aud_df,

        dtformat=('%d.%m.%Y %H:%M:%S.%f'),
        openinterest=-1
    )

    eur_df = pd.read_csv(EUR_MID_PATH, index_col=0, parse_dates=True)
    # print(eur_df.head())
    eur_data = bt.feeds.PandasDirectData(

        dataname=eur_df,

        dtformat=('%d.%m.%Y %H:%M:%S.%f'),
        openinterest=-1
    )

    gbp_df = pd.read_csv(GBP_MID_PATH, index_col=0, parse_dates=True)
    # print(gbp_df.head())
    gbp_data = bt.feeds.PandasDirectData(

        dataname=gbp_df,

        dtformat=('%d.%m.%Y %H:%M:%S.%f'),
        openinterest=-1
    )
    # Add the EUR/USD Data Feed to Cerebro

    cb.resampledata(eur_data, name="EUR",
                    timeframe=bt.TimeFrame.Minutes, compression=1)

    # Add the LIGHT OIL Data Feed to Cerebro

    cb.resampledata(gbp_data, name="GBP",
                    timeframe=bt.TimeFrame.Minutes, compression=1)

    cb.resampledata(aud_data, name="AUD",
                    timeframe=bt.TimeFrame.Minutes, compression=1)

    # initializing the params

    strat_params = {
        'eur_stoploss': 3000,
        'eur_takeprofit': 3000,
        "eur_open_count": 10,
        "eur_close_count": 5,
        'aud_stoploss': 3000,
        'aud_takeprofit': 3000,
        "aud_open_count": 10,
        "aud_close_count": 5,
        'gbp_stoploss': 3000,
        'gbp_takeprofit': 3000,
        "gbp_open_count": 10,
        "gbp_close_count": 5,
    }
    # Add MyStrat to Cerebro

    cb.addstrategy(MyStrategy)

    # Add comission and margin to Cerebro
    # cb.broker.setcommission(commission=2.42, margin=8600.0,
    #                         mult=1000.0, name='Light_Oil')

    # print('Starting Portfolio Value: %.2f' % cb.broker.getvalue())

    cb.run()

    # print('Final Portfolio Value: %.2f' % cb.broker.getvalue())

    # log_repot()


if __name__ == '__main__':
    start()
