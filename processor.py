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

    return get_model_results('bollinger')


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
