"""
    Processing model results to UI compatible format
"""

import logging

import pandas as pd

from stock_common.lib.database import Database
from stock_common.conf.config import Config

CONFIGS = Config.get_configs()
DB = Database(CONFIGS)


def bollinger():
    """
        processor for bollinger model
    """

    model_results = _get_model_results('bollinger')

    df = pd.DataFrame(model_results)

    df['analyses'] = df.details.apply(_format_dict_to_html)
    del df['details']

    return df
    

@DB.connect('MONGO')
def _get_model_results(client, model):
    """
        Getting Bollinger Model Results From Mongo
    """

    logging.info('Getting {} Model Results From MONGO'.format(model))
    database = client.stock_recommender
    last_trading_day = list(database.prices.find(
        {}, {'date': 1, '_id': 0}).sort('date', -1).limit(1))[0]['date']
    model_results = list(database.model_results.find(
        {"created_at": last_trading_day, "model": model}
    ))

    return model_results


def _format_dict_to_html(dct):
    """
        Formatting Dictionary to HTML
    """

    lines = ''
    for key, value in dct.items():
        lines += """<div class="row">{0}：{1}</div>""".format(key, value)

    return lines
