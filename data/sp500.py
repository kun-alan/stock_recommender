"""
    sp500 symbols
"""

import urllib.request
import datetime
from collections import OrderedDict

from bs4 import BeautifulSoup

from stock_common.conf.config import Config
from stock_common.lib.database import Database

CONFIGS = Config.get_configs()
logging = CONFIGS.get_logging()
db = Database(CONFIGS)


class SP500():
    """
    SP500 class that scraping sp500 symbols from wikipeia
    """
    def __init__(self):
        self.url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        self.mongo_schema = 'stock_recommender'
        self.mongo_collection = 'ticker_symbols'

    def get_symbols_from_wikipedia(self):
        """
        Request wikipedia url and parse the html to get sp500 symbols

        Returns:
            a list of dict
        """
        header = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(self.url, headers=header)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'lxml')

        table = soup.find('table', {'class': 'wikitable sortable'})
        rows = table.findAll('tr')

        now = datetime.datetime.now()

        header = [
            'symbol', 'security', 'sec_filings', 'sector', 'sub_industry',
            'address', 'first_added_date', 'cik'
        ]

        symbols = []
        for row in rows:
            col = row.findAll('td')
            if col:
                values = [
                    None if value.string is None
                    else value.string.strip() for value in col
                ]
                data = OrderedDict(zip(header, values))
                if data['first_added_date']:
                    first_added_date = datetime.datetime.strptime(
                        data['first_added_date'], '%Y-%m-%d')
                else:
                    first_added_date = None

                symbol = {
                    '_id': data['symbol'],
                    'symbol': data['symbol'],
                    'security': data['security'],
                    'sector': data['sector'],
                    'industry': data['sub_industry'],
                    'address': data['address'],
                    'first_added_date': first_added_date,
                    'central_index_key': data['cik'],
                    'last_updated': now,
                    'source': 'sp500',
                }

                symbols.append(symbol)

        return symbols

    @db.connect('MONGO')
    def upsert_symbols_into_mongo(self, client):
        """
        Upserting sp500 symbols into mongo
        """
        collection = client[self.mongo_schema][self.mongo_collection]
        symbols = self.get_symbols_from_wikipedia()

        for symbol in symbols:
            collection.replace_one({'_id': symbol['_id']}, symbol, upsert=True)

    @db.connect('MONGO')
    def get_symbols_from_mongo(self, client, details=False):
        """
        Getting SP500 symbols from Mongo
        """
        collection = client[self.mongo_schema][self.mongo_collection]

        if details:
            return list(collection.find())
        else:
            symbols = list(collection.find(
                {'symbol': 1, '_id': 0}
            ))
            return [item['symbol'] for item in symbols]
