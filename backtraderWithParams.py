import os

import sys

import numpy as np
import pandas as pd

import backtrader as bt
from datetime import datetime

AUD_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\AUD_USD\MID\AUD_USD_MID.csv"
EUR_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\EUR_USD\MID\EUR_USD_MID.csv"
GBP_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\GBP_USD\MID\GBP_USD_MID.csv"


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
        pass
        # print(self.params.eur_stoploss)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])

        print('%s, %s' % (dt.isoformat(), txt))


def start():

    cb = bt.Cerebro()

    cb.broker.set_cash(1000000)

    print("Cerebro created")

    aud_df = pd.read_csv(AUD_MID_PATH, index_col=0, parse_dates=True)
    print(aud_df.head())
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
    print(gbp_df.head())
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

    cb.addstrategy(MyStrategy, params=strat_params)

    # Add comission and margin to Cerebro
    # cb.broker.setcommission(commission=2.42, margin=8600.0,
    #                         mult=1000.0, name='Light_Oil')

    # print('Starting Portfolio Value: %.2f' % cb.broker.getvalue())

    cb.run()

    # print('Final Portfolio Value: %.2f' % cb.broker.getvalue())

    # log_repot()


if __name__ == '__main__':
    start()
