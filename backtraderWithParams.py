import os

import sys

import numpy as np
import pandas as pd

import backtrader as bt
from datetime import datetime


PROFIT_LOSS_DICT = {}
MAXDRAWDOWN = 0

AUD_MID_PATH = r"datas/AUD_USD/MID/AUD_USD_MID.csv"
EUR_MID_PATH = r"datas/EUR_USD/MID/EUR_USD_MID.csv"
GBP_MID_PATH = r"datas/GBP_USD/MID/GBP_USD_MID.csv"


class MyStrategy(bt.Strategy):
    params = (
        ('strat_params', None),
    )

    def __init__(self):
        if self.params != None:
            for name, val in self.params.strat_params.items():
                print(name, val)
                setattr(self.params, name, val)

        self.counter = -1
        self.order = None

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
                    f'BUY EXECUTED on {order.data._name}, Price: %.4f, Size: %.2f, Position = %.2f' %
                    (
                        order.executed.price,
                        order.executed.size,
                        self.getposition(order.data).size
                    )
                )
            else:
                # Sell
                self.log(
                    f'SELL EXECUTED on {order.data._name}, Price: %.4f, Size: %.2f, Position = %.2f' %
                    (
                        order.executed.price,
                        order.executed.size,
                        self.getposition(order.data).size
                    )
                )
        elif order.status in [order.Canceled]:
            # self.log(
            pass
            #     f'{order.price} ON  {order.data._name} Order Canceleds ')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        if bt.num2date(trade.data.datetime[0]).date().__str__() in PROFIT_LOSS_DICT:
            PROFIT_LOSS_DICT[bt.num2date(trade.data.datetime[0]).date().__str__()
                             ] += trade.pnl
        else:
            PROFIT_LOSS_DICT[bt.num2date(trade.data.datetime[0]).date().__str__()
                             ] = trade.pnl

        self.log('OPERATION PROFIT, GROSS %.2f' % trade.pnl)

    def get_limitprice(self, close_price, d_name):
        if d_name == "EUR":
            take_profit = self.p.eur_takeprofit
        elif d_name == "AUD":
            take_profit = self.p.aud_takeprofit
        else:
            take_profit = self.p.gbp_takeprofit
        profit_per_one = take_profit / 300000
        limitprice = close_price + profit_per_one
        return limitprice

    def get_stopprice(self, close_price, d_name):
        if d_name == "EUR":
            stoploss = self.p.eur_stoploss
        elif d_name == "AUD":
            stoploss = self.p.aud_stoploss
        else:
            stoploss = self.p.gbp_stoploss
        loss_per_one = stoploss / 300000
        stopprice = close_price - loss_per_one
        return stopprice

    def check_open_close_count(self, hist_data):
        if hist_data._name == "EUR":
            return (
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.eur_open_count)),
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.eur_close_count)),
                self.getposition(hist_data).size)
        elif hist_data._name == "AUD":
            return (
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.aud_open_count)),
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.aud_close_count)),
                self.getposition(hist_data).size)
        else:
            return (
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.gbp_open_count)),
                np.diff(
                    hist_data.close.get(ago=0, size=self.p.gbp_close_count)),
                self.getposition(hist_data).size
            )

    def set_order(self, hist_data):
        bracket_sell = None
        bracket_buy = None
        open_count, close_count, pos = self.check_open_close_count(
            hist_data)
        # self.check_open_close_count(hist_data)
# -------------------- Buy ON rise
        if np.all(open_count > 0) and (not pos):
            bracket_buy = self.buy_bracket(data=hist_data, size=300000,
                                           price=hist_data.close[0],
                                           exectype=bt.Order.Market,
                                           limitprice=self.get_limitprice(
                                               hist_data.close[0], hist_data._name),
                                           stopprice=self.get_stopprice(
                                               hist_data.close[0], hist_data._name)
                                           )
            self.log(
                f"BUY Order On {hist_data._name}, on Price %.4f" % hist_data.close[0])
# ----------------------Close ON Rise
        elif np.all(close_count > 0) and pos:
            if bracket_sell:
                self.cancel(bracket_sell[1])
                self.cancel(bracket_sell[2])
                bracket_sell = None
            if bracket_buy:
                self.cancel(self.bracket_buy[1])
                self.cancel(self.bracket_buy[2])
                bracket_buy = None
            self.close(data=hist_data)
            self.log(
                f"CLOSE Order On {hist_data._name}, %.4f" % hist_data.close[0])
#  -----------------------------Sell ON fall
        if np.all(open_count < 0) and (not pos):
            bracket_sell = self.sell_bracket(data=hist_data, size=-300000,
                                             price=hist_data.close[0],
                                             exectype=bt.Order.Market,
                                             stopprice=self.get_limitprice(
                                                 hist_data.close[0], hist_data._name),
                                             limitprice=self.get_stopprice(
                                                 hist_data.close[0], hist_data._name)
                                             )
            self.log(
                f"SELL Order On {hist_data._name}, on Price %.4f" % hist_data.close[0])
# Close on fall
        elif np.all(close_count < 0) and pos:
            if bracket_sell:
                self.cancel(bracket_sell[1])
                self.cancel(bracket_sell[2])
                bracket_sell = None
            if bracket_buy:
                self.cancel(self.bracket_buy[1])
                self.cancel(self.bracket_buy[2])
                bracket_buy = None
            self.close(data=hist_data)
            self.log(
                f"CLOSE Order On {hist_data._name}, %.4f" % hist_data.close[0])

    def next(self):
        self.counter += 1
        if self.counter < 10:
            return

        for hist_data in self.datas:
            # print(hist_data.close[0])
            self.set_order(hist_data)


def report_writer(mdd):
    values = np.array(list(PROFIT_LOSS_DICT.values()))
    with open(r"reports/strategy_report.txt", 'w') as r:
        r.write("profit and los : \n")
        for key, value in PROFIT_LOSS_DICT.items():
            r.write(f"{key, value}")
            r.write("\n")

        r.write("Avg PnL : ")
        r.write(f"{np.mean(values)}")
        r.write("\n")
        r.write("Std PnL : ")
        r.write(f"{np.std(values)}")
        r.write("\n")
        r.write("MaxDrawDown : ")
        r.write(f"{mdd}")


def start():

    cb = bt.Cerebro()

    cb.broker.set_cash(1000000)

    print("Cerebro created")

    aud_df = pd.read_csv(AUD_MID_PATH, index_col=0, parse_dates=True)
    # print(aud_df.head())
    for date in aud_df.index.date:
        PROFIT_LOSS_DICT[date.__str__()] = 0
    aud_data = bt.feeds.PandasDirectData(

        dataname=aud_df,

        dtformat=('%d.%m.%Y %H:%M:%S.%f'),
        openinterest=-1
    )

    eur_df = pd.read_csv(EUR_MID_PATH, index_col=0, parse_dates=True)
    print(eur_df.head())
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

    cb.addstrategy(MyStrategy, strat_params=strat_params)

    # Add comission and margin to Cerebro
    # cb.broker.setcommission(commission=2.42, margin=8600.0,
    #                         mult=1000.0, name='Light_Oil')
    cb.addanalyzer(bt.analyzers.DrawDown, _name='mydrawndown')
# print('Starting Portfolio Value: %.2f' % cb.broker.getvalue())

    strat = cb.run()

# print('Final Portfolio Value: %.2f' % cb.broker.getvalue())

    report_writer(strat[0].analyzers.mydrawndown.get_analysis().max.moneydown)


if __name__ == '__main__':
    start()
