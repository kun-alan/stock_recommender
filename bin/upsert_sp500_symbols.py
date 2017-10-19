#!/usr/bin/env python
"""
    Scraping SP500 Symbols, and upsert to MongoDB
"""

from stock_recommender.data.sp500 import SP500


def main():
    sp500 = SP500()
    sp500.upsert_symbols_into_mongo()


if __name__ == '__main__':
    main()
