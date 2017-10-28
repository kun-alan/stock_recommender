"""
    Processor for UI
"""

import logging

from stock_common.lib.database import Database
from stock_common.conf.config import Config

CONFIGS = Config.get_configs()
db = Database(CONFIGS)


def bollinger():
    """
        processor for bollinger model
    """

    model_results = get_model_results('bollinger')

    new_results = []

    for result in model_results:
        new = {
            'symbol': result['symbol'],
            'date_to_buy': result['date_to_buy'],
            'Blg Pre': round(result['details']['equity_bollinger_yesterday'], 2),
            'Blg Now': round(result['details']['equity_bollinger_today'], 2),
            'SPX Blg': round(result['details']['spx_bollinger_today'], 2),
        }
        new_results.append(new)

    return new_results


def volatility():
    """
        processor for volatility model
    """

    return get_model_results('volatility')


@db.connect('MONGO')
def get_model_results(client, model):
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
