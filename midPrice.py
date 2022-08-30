import pandas as pd
import numpy as np


AUD_ASK_PATH = r"datas/AUD_USD/ASKAUDUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
AUD_BID_PATH = r"datas/AUD_USD/BIDAUDUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
AUD_MID_PATH = r"datas/AUD_USD/MIDAUD_USD_MID.csv"

EUR_ASK_PATH = r"datas/EUR_USD/ASKEURUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
EUR_BID_PATH = r"datas/EUR_USD/BIDEURUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
EUR_MID_PATH = r"datas/EUR_USD/MIDEUR_USD_MID.csv"

GBP_ASK_PATH = r"datas/GBP_USD/ASKGBPUSD_Candlestick_1_M_ASK_01.07.2022-01.08.2022.csv"
GBP_BID_PATH = r"datas/GBP_USD/BIDGBPUSD_Candlestick_1_M_BID_01.07.2022-01.08.2022.csv"
GBP_MID_PATH = r"datas/GBP_USD/MIDGBP_USD_MID.csv"


def get_mid_price_from_ask_bid(ask_path, bid_path):
    ask_df = pd.read_csv(ask_path, index_col=0, parse_dates=True)
    print(ask_df.head())
    bid_df = pd.read_csv(bid_path, index_col=0, parse_dates=True)
    print(bid_df.head())
    # Gmt_time, Open, High, Low, Close, Volume
    ask_df = ask_df.add(bid_df)
    ask_df = ask_df.div(2)
    # mid_df["open"] = mid_df =
    print("MID_PRICE")
    print(ask_df.head())
    return ask_df


aud_mid_df = get_mid_price_from_ask_bid(AUD_ASK_PATH, AUD_BID_PATH)
aud_mid_df.to_csv(AUD_MID_PATH)

gbp_mid_df = get_mid_price_from_ask_bid(GBP_ASK_PATH, GBP_BID_PATH)
gbp_mid_df.to_csv(GBP_MID_PATH)

eur_mid_df = get_mid_price_from_ask_bid(EUR_ASK_PATH, EUR_BID_PATH)
eur_mid_df.to_csv(EUR_MID_PATH)
