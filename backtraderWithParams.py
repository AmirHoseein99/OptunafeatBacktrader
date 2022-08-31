from datetime import datetime
import backtrader as bt
import pandas as pd
import numpy as np
import optuna
import sys
import os
from sqlalchemy import create_engine


ASSETS_NAMES = ["EUR", "AUD", "GBP"]
ASSETS_PATHES = {
    "EUR": r"datas/AUD_USD/MID/AUD_USD_MID.csv",
    "AUD": r"datas/EUR_USD/MID/EUR_USD_MID.csv",
    "GBP": r"datas/GBP_USD/MID/GBP_USD_MID.csv"
}
ASSETS_DATAS = {
    "EUR": None,
    "AUD": None,
    "GBP": None
}
ASSETS_DFS = {
    "EUR": None,
    "AUD": None,
    "GBP": None
}
PROFIT_LOSS_DICT = {}
MAXDRAWDOWN = 0


stop_loss_params = {}
take_profit_params = {}
open_count_params = {}
close_count_params = {}
size_params = {}


class MyStrategy(bt.Strategy):
    params = (
        ('strat_params', None),
    )

    def __init__(self):
        if self.params != None:
            for name, val in self.params.strat_params.items():
                # print(name, val)
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
                # self.log(
                #     f'BUY EXECUTED on {order.data._name}, Price: %.4f, Size: %.2f, Position = %.2f' %
                #     (
                #         order.executed.price,
                #         order.executed.size,
                #         self.getposition(order.data).size
                #     )
                # )
                pass
            else:
                pass
                # Sell
                # self.log(
                #     f'SELL EXECUTED on {order.data._name}, Price: %.4f, Size: %.2f, Position = %.2f' %
                #     (
                #         order.executed.price,
                #         order.executed.size,
                #         self.getposition(order.data).size
                #     )
                # )
        elif order.status in [order.Canceled]:
            pass

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        if bt.num2date(trade.data.datetime[0]).date().__str__() in PROFIT_LOSS_DICT:
            PROFIT_LOSS_DICT[bt.num2date(
                trade.data.datetime[0]).date().__str__()] += trade.pnl
        else:
            PROFIT_LOSS_DICT[bt.num2date(
                trade.data.datetime[0]).date().__str__()] = trade.pnl

    def get_upperprice(self, close_price, d_name):
        take_profit = self.p.takeprofit[d_name]
        profit_per_one = take_profit / self.p.size[d_name]
        limitprice = close_price + profit_per_one
        return limitprice

    def get_lowerprice(self, close_price, d_name):
        stop_loss = self.p.stoploss[d_name]
        profit_per_one = stop_loss / self.p.size[d_name]
        limitprice = close_price - profit_per_one
        return limitprice

    def check_open_close_count(self, hist_data):
        return (
            np.diff(
                hist_data.close.get(ago=0, size=self.p.open_count[hist_data._name])),
            np.diff(
                hist_data.close.get(ago=0, size=self.p.open_count[hist_data._name])),
            self.getposition(hist_data).size)

    def set_order(self, hist_data):
        bracket_sell = None
        bracket_buy = None
        open_count, close_count, pos = self.check_open_close_count(hist_data)

# ------------------------------------------ Buy ON rise-------------------------------------------
        if np.all(open_count > 0) and (not pos):
            bracket_buy = self.buy_bracket(data=hist_data, size=self.p.size[hist_data._name],
                                           price=hist_data.close[0],
                                           exectype=bt.Order.Market,
                                           limitprice=self.get_upperprice
                                           (
                                               hist_data.close[0], hist_data._name),
                                           stopprice=self.get_lowerprice(
                                               hist_data.close[0], hist_data._name)
                                           )
            # self.log(
            #     f"BUY Order On {hist_data._name}, on Price %.4f" % hist_data.close[0])
# ------------------------------------------Close ON Rise------------------------------------------
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
            # self.log(
            #     f"CLOSE Order On {hist_data._name}, %.4f" % hist_data.close[0])
# ------------------------------------------Sell ON fall------------------------------------------------------------
        if np.all(open_count < 0) and (not pos):
            bracket_sell = self.sell_bracket(data=hist_data, size=-self.p.size[hist_data._name],
                                             price=hist_data.close[0],
                                             exectype=bt.Order.Market,
                                             stopprice=self.get_upperprice
                                             (
                                                 hist_data.close[0], hist_data._name),
                                             limitprice=self.get_lowerprice(
                                                 hist_data.close[0], hist_data._name)
                                             )
            # self.log(
            # f"SELL Order On {hist_data._name}, on Price %.4f" % hist_data.close[0])
# ------------------------------------------------Close on fall--------------------------------------
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
            # self.log(
            # f"CLOSE Order On {hist_data._name}, %.4f" % hist_data.close[0])

    def next(self):
        self.counter += 1
        if self.counter < 10:
            return

        for hist_data in self.datas:
            # print(hist_data.close[0])
            self.set_order(hist_data)


def run_backtest(optuna_params):

    cb = bt.Cerebro()

    cb.broker.set_cash(1000000)
    for name in ASSETS_NAMES:
        ASSETS_DFS[name] = pd.read_csv(
            ASSETS_PATHES[name], index_col=0, parse_dates=True)

        ASSETS_DATAS[name] = bt.feeds.PandasDirectData(

            dataname=ASSETS_DFS[name],

            dtformat=('%d.%m.%Y %H:%M:%S.%f'),
            openinterest=-1
        )
        cb.resampledata(ASSETS_DATAS[name], name=name,
                        timeframe=bt.TimeFrame.Minutes,
                        compression=1)

    # Add MyStrat to Cerebro

    cb.addstrategy(MyStrategy, strat_params=optuna_params)

    # Add comission and margin to Cerebro
    # cb.broker.setcommission(commission=2.42, margin=8600.0,
    #                         mult=1000.0, name='Light_Oil')
    cb.addanalyzer(bt.analyzers.DrawDown, _name='mydrawndown')
# print('Starting Portfolio Value: %.2f' % cb.broker.getvalue())

    strat = cb.run()

    # report_writer(strat[0].analyzers.mydrawndown.get_analysis().max.moneydown)
# print('Final Portfolio Value: %.2f' % cb.broker.getvalue())

    # report_writer()


# stop_loss_params = {}
# take_profit_params = {}
# open_count_params = {}
# close_count_params = {}
# size_params = {}


def objective_func(trial):

    for name in ASSETS_NAMES:
        open_count_params[name] = trial.suggest_int(
            f"{name}_open_count", 3, 28, step=5)
        close_count_params[name] = trial.suggest_int(
            f"{name}_close_count", 2, 22, step=5)
        stop_loss_params[name] = trial.suggest_float(
            f"{name}_stoploss", 500, 2500, step=500)
        take_profit_params[name] = trial.suggest_float(
            f"{name}_takeprofit", 500, 2500, step=500)
        size_params[name] = trial.suggest_int(
            f"{name}_size", 100000, 300000, step=50000)

    run_backtest({
        'stoploss': stop_loss_params,
        'takeprofit': take_profit_params,
        "open_count": open_count_params,
        "close_count": close_count_params,
        "size": size_params
    }
    )

    daily_profit_avg = np.mean(np.array(list(PROFIT_LOSS_DICT.values())))
    daily_profit_std = np.std(np.array(list(PROFIT_LOSS_DICT.values())))

    return daily_profit_avg, daily_profit_std


if __name__ == '__main__':

    optuna.logging.set_verbosity(optuna.logging.INFO)

    storage_name = "postgresql://postgres:newpassword@localhost/optunamultiobjdb"

    # sqlite:///BackTest_Params_Search.db
    back_test_study = optuna.create_study(
        directions=["maximize", "minimize"],
        storage=storage_name,
        load_if_exists=True,
        sampler=optuna.samplers.MOTPESampler(n_startup_trials=1000),
        # pruner=optuna.pruners.HyperbandPruner(),
        study_name="BackTest_Params_Search")
    # db file + load if exists
    back_test_study.optimize(objective_func, n_trials=3000)
    report_writer()
    best_trial = back_test_study.best_trials
    print("Best value: ", best_trial.value)
    print("Parameters that achieve the best value: ", best_trial.params)


def report_writer(trail_num):
    values = np.array(list(PROFIT_LOSS_DICT.values()))
    profit_loss_df = pd.DataFrame.from_dict([date, pnl], PROFIT_LOSS_DICT)
    print(profit_loss_df.head())

    # # with open(r"reports/strategy_report.txt", 'w') as r:
    # #     r.write("profit and los : \n")
    # #     for key, value in PROFIT_LOSS_DICT.items():
    # #         r.write(f"{key, value}")
    # #         r.write("\n")
