#!/usr/bin/env python
import argparse

from kicktipp import Kicktipp


def main():
    args = parse_args()
    kicktipp = Kicktipp(args)
    kicktipp.handle_matchday(args.matchday)
    kicktipp.kill_browser()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-v", "--verbose", action="count", help="increase output verbosity", required=False)
    argparser.add_argument("-x", "--show_browser", help="show the browser doing his work",
                           action="store_true", required=False)
    argparser.add_argument("-u", "--username", help="Username for Kicktipp login", required=True)
    argparser.add_argument("-p", "--password", help="Password for Kicktipp login", required=True)
    argparser.add_argument("-m", "--matchday", help="Number of the matchday to bet for", type=int, default=1)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    main()
