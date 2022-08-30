import pandas as pd
import numpy as np


AUD_ASK_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\AUD_USD\ASK\AUDUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
AUD_BID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\AUD_USD\BID\AUDUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
AUD_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\AUD_USD\MID\AUD_USD_MID.csv"

EUR_ASK_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\EUR_USD\ASK\EURUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
EUR_BID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\EUR_USD\BID\EURUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
EUR_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\EUR_USD\MID\EUR_USD_MID.csv"

GBP_ASK_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\GBP_USD\ASK\GBPUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
GBP_BID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\GBP_USD\BID\GBPUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
GBP_MID_PATH = r"C:/Users\Amiri\OneDrive\Desktop\StrategyWithParamSearch\datas\GBP_USD\MID\GBP_USD_MID.csv"


def get_mid_price_from_ask_bid(ask_path, bid_path):
    ask_df = pd.read_csv(ask_path, index_col=0, parse_dates=True)
    print(ask_df.head())
    bid_df = pd.read_csv(bid_path, index_col=0, parse_dates=True)
    print(bid_df.head())
    # Gmt_time, Open, High, Low, Close, Volume
    mid_df = pd.DataFrame()
    mid_df["gmttime"] = ask_df.iloc[:, 0]
    mid_df = pd.concat(
        [mid_df,  ask_df.iloc[:, 1:].add(bid_df.iloc[:, 1:])], axis=1)
    mid_df.iloc[:, 1:] = mid_df.iloc[:, 1:].div(2)
    print("MID_PRICE")
    print(mid_df.head())
    return mid_df


aud_mid_df = get_mid_price_from_ask_bid(AUD_ASK_PATH, AUD_BID_PATH)
aud_mid_df.to_csv(AUD_MID_PATH)

gbp_mid_df = get_mid_price_from_ask_bid(GBP_ASK_PATH, GBP_BID_PATH)
gbp_mid_df.to_csv(GBP_MID_PATH)

eur_mid_df = get_mid_price_from_ask_bid(EUR_ASK_PATH, EUR_BID_PATH)
eur_mid_df.to_csv(EUR_MID_PATH)
