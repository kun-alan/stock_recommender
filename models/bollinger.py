#!/usr/bin/env python
"""
    Bollinger Model
"""

import logging
import datetime

import pandas as pd

from stock_common.lib import util
from stock_common.lib.database import Database
from stock_common.conf.config import Config
from stock_recommender.data.sp500 import SP500

CONFIGS = Config.get_configs()
db = Database(CONFIGS)


def bollinger():
    """
        Bollinger value for the equity today <= -2.0
        Bollinger value for the equity yesterday >= -2.0
        Bollinger value for SPY today >= 1.2
    """
    symbols = SP500().get_symbols_from_mongo()

    if 'SPY' not in symbols:
        symbols.append('SPY')

    end_date = get_last_trading_date()

    pf_price = pd.read_hdf('../tmp/' + CONFIGS.PRICES_H5)
    df_close = pf_price.Close.tail(21).dropna(axis=1)

    assert end_date == df_close.index[-1].date()

    df_ma = df_close.rolling(window=20,center=False).mean().tail(2)
    df_std = df_close.rolling(window=20,center=False).std().tail(2)
    df_bollingerbands = (df_close.tail(2) - df_ma) / df_std

    todays_symbols = df_bollingerbands.columns.tolist()

    df_bollingerbands.sort_index(inplace=True)

    model_results = []
    SPY = df_bollingerbands.iloc[1]['SPY']

    date_to_sell = end_date + datetime.timedelta(days=5)
    for symbol in todays_symbols:
        yesterday = df_bollingerbands.iloc[0][symbol]
        today = df_bollingerbands.iloc[1][symbol]
        if yesterday >= -2.0 and today <= -2.0 and SPY >= 1.2:
            model_result = {
                'symbol': symbol,
                'date_to_buy': util.date_to_int(end_date),
                'holding_period': '5days',
                'date_to_sell': util.date_to_int(date_to_sell),
                'model': 'bollinger',
                'created_at': util.date_to_int(end_date),
                'details': {
                    'lookback': '20days',
                    'equity_bollinger_yesterday': yesterday,
                    'equity_bollinger_today': today,
                    'spx_bollinger_today': SPY,
                }
            }
            model_results.append(model_result)

    if not model_results:
        logging.info('No stock to recommend today. SPY: {}'.format(SPY))
    return model_results


def get_last_trading_date():
    """
        return today if past 4pm, else return yesterday
    """

    today = datetime.datetime.today()
    if today.hour >= 16:
        return today.date()
    else:
        return today.date() - datetime.timedelta(days=1)


if __name__ == '__main__':
    logging = CONFIGS.get_logging()
    model_results = bollinger()
    if model_results:
        util.insert_documents_to_mongo(
            db='stock_recommender',
            collection='model_results',
            documents=model_results
        )
