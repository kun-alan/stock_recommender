#!/usr/bin/env python
"""
    Scraping SP500 Symbols, and upsert to MongoDB
"""

from stock_common.conf.config import Config
from stock_recommender.data.sp500 import SP500

CONFIGS = Config.get_configs()
logging = CONFIGS.get_logging()


def main():
    logging.info('Updating SP500 Symbols and Prices')
    sp500 = SP500()
    logging.info('Getting Symbols')
    sp500.upsert_symbols_into_mongo()
    logging.info('Updating Prices')
    sp500.refresh_historical_prices()


if __name__ == '__main__':
    main()
