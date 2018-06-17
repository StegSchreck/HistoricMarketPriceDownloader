#!/usr/bin/env python
import argparse

from kicktipp import Kicktipp


def main():
    args = parse_args()
    kicktipp = Kicktipp(args)
    for matchday in args.matchday:
        kicktipp.handle_matchday(args.community, int(matchday))
    kicktipp.browser_handler.kill()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-v", "--verbose", action="count", help="increase output verbosity", required=False)
    argparser.add_argument("-x", "--show_browser", help="show the browser doing his work",
                           action="store_true", required=False)
    argparser.add_argument("-c", "--community", help="Kicktipp prediction community", required=True)
    argparser.add_argument("-u", "--username", help="Username for Kicktipp login", required=True)
    argparser.add_argument("-p", "--password", help="Password for Kicktipp login", required=True)
    argparser.add_argument("-m", "--matchday", help="Number of the matchday to bet for", required=True, action='append')
    argparser.add_argument("-d", "--dryrun", action="store_true", required=False,
                           help="Do not insert into Kicktipp, only print calculated results on console")
    argparser.add_argument("-r", "--random", help="Generate random scores and ignore betting odds",
                           action="store_true", required=False)
    argparser.add_argument("-a", "--anti", help="Generate scores by favoring the underdog according to betting odds",
                           action="store_true", required=False)
    argparser.add_argument("-s", "--static", help="Generate static scores", required=False)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    main()
