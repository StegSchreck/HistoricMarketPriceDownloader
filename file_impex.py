import datetime
import os
import sys
import time
from typing import Dict

CSV_HEADER = 'Datum;Kurs\n'


def save_market_prices_to_csv(market_prices: Dict[str, str], folder: str, filename: str):
    sys.stdout.write('===== saving market prices to CSV\r\n')
    sys.stdout.write('      folder: {}\r\n'.format(folder))
    sys.stdout.write('      filename: {}\r\n'.format(filename))
    sys.stdout.write('      number of entries: {}\r\n'.format(len(market_prices)))
    sys.stdout.flush()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+', encoding='UTF-8') as output_file:
        output_file.write(CSV_HEADER)
        for date, value in market_prices.items():
            output_file.write(convert_market_price_entry_to_csv_row(date, value))


def convert_market_price_entry_to_csv_row(date, value):
    return f"{date}; {value}\n"
