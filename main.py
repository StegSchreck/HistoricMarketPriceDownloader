#!/usr/bin/env python
import argparse
import os
import time
from datetime import datetime

import file_impex
from ariva import Ariva

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'exports'))
TIMESTAMP = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


def main():
    args = parse_args()
    ariva = Ariva(args)
    for isin in args.isin:
        market_prices = ariva.download(isin, args.market_place)
        filename = args.filename if args and args.filename else f"{TIMESTAMP}_{isin}.csv"
        file_impex.save_market_prices_to_csv(market_prices=market_prices, folder=args.destination, filename=filename)
    ariva.browser_handler.kill()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-v", "--verbose", help="increase output verbosity", required=False, action="count")
    argparser.add_argument("-x", "--show_browser", help="show the browser doing his work",
                           action="store_true", required=False)
    argparser.add_argument("-i", "--isin", help="ISIN of the stock", action='append', required=True)
    argparser.add_argument("-u", "--username", help="Username or email for ariva login", required=True)
    argparser.add_argument("-p", "--password", help="Password for ariva login", required=True)
    argparser.add_argument("-m", "--market_place", help="Name of the marketplace to use", required=False, default=None)
    argparser.add_argument("-d", "--destination", help="destination folder for result CSV file", required=False,
                           default=EXPORTS_FOLDER)
    argparser.add_argument("-f", "--filename", help="filename for the result CSV", required=False)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    main()
