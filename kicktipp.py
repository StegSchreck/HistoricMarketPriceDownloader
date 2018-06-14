import math
import sys
import time
from collections import namedtuple

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from bash_color import BashColor
from browser_handler import BrowserHandler


class Kicktipp:
    def __init__(self, args):
        self.args = args

        login_form_selector = "//form[@id='loginFormular']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='kennung']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='passwort']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"

        self._init_browser()

    def _init_browser(self):
        self.browser_handler = BrowserHandler(self.args)
        self.browser = self.browser_handler.browser
        self.login()

    def login(self):
        self.browser.get("https://www.kicktipp.de/info/profil/login")
        time.sleep(1)

        iteration = 0
        while self._user_is_not_logged_in():
            iteration += 1
            try:
                self._insert_login_credentials()
                self._click_login_button()
            except NoSuchElementException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue
            if iteration > 2:
                self._handle_login_unsuccessful()

    def _user_is_not_logged_in(self):
        return len(self.browser.find_elements_by_xpath(self.LOGIN_BUTTON_SELECTOR)) > 0 \
               and len(self.browser.find_elements_by_xpath(self.LOGIN_USERNAME_SELECTOR)) > 0 \
               and len(self.browser.find_elements_by_xpath(self.LOGIN_PASSWORD_SELECTOR)) > 0

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element_by_xpath(self.LOGIN_USERNAME_SELECTOR)
        login_field_user.clear()
        login_field_user.send_keys(self.args.username)
        login_field_password = self.browser.find_element_by_xpath(self.LOGIN_PASSWORD_SELECTOR)
        login_field_password.clear()
        login_field_password.send_keys(self.args.password)

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath(self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(2)  # wait for page to load

    def _handle_login_unsuccessful(self):
        time.sleep(1)
        if self._user_is_not_logged_in():
            sys.stderr.write("Login to Kicktipp failed.")
            sys.stdout.flush()
            self.browser_handler.kill()
            sys.exit(1)

    def handle_matchday(self, community, matchday):
        self.go_to_matchday(community, matchday)
        matches = self.retrieve_betting_odds()
        self.calculate_tips(matches)
        if self.args and (self.args.dryrun or (self.args.verbose and self.args.verbose >= 1)):
            tail = '#' * 75
            print(BashColor.BOLD + "### MATCHDAY {matchday: >2} {tail}".format(matchday=matchday, tail=tail) + BashColor.END)
            for match in matches:
                odds_home_marker, odds_draw_marker, odds_guest_marker = self._define_markers(match)
                print("{home_team: >15} - {guest_team: <15}\t"
                      "{odds_home_marker}{odds_home: 7.2f}{marker_end} "
                      "{odds_draw_marker}{odds_draw: 7.2f}{marker_end} "
                      "{odds_guest_marker}{odds_guest: 7.2f}{marker_end}\t\t"
                      "{tip_marker}[{tip_home: >2} :{tip_guest: >2} ]{marker_end}".format(
                          home_team=match.home_team,
                          guest_team=match.guest_team,
                          odds_home_marker=odds_home_marker,
                          odds_draw_marker=odds_draw_marker,
                          odds_guest_marker=odds_guest_marker,
                          odds_home=match.odds_home,
                          odds_draw=match.odds_draw,
                          odds_guest=match.odds_guest,
                          tip_home=match.tip_home,
                          tip_guest=match.tip_guest,
                          tip_marker=BashColor.BLUE,
                          marker_end=BashColor.END
                      ))
        if self.args and not self.args.dryrun:
            self.enter_tips(matches)

    @staticmethod
    def _define_markers(match):
        odds_home_marker = BashColor.YELLOW
        odds_draw_marker = BashColor.YELLOW
        odds_guest_marker = BashColor.YELLOW
        if match.odds_home == min(match.odds_home, match.odds_draw, match.odds_guest):
            odds_home_marker = BashColor.GREEN
        elif match.odds_home == max(match.odds_home, match.odds_draw, match.odds_guest):
            odds_home_marker = BashColor.RED
        if match.odds_draw == min(match.odds_home, match.odds_draw, match.odds_guest):
            odds_draw_marker = BashColor.GREEN
        elif match.odds_draw == max(match.odds_home, match.odds_draw, match.odds_guest):
            odds_draw_marker = BashColor.RED
        if match.odds_guest == min(match.odds_home, match.odds_draw, match.odds_guest):
            odds_guest_marker = BashColor.GREEN
        elif match.odds_guest == max(match.odds_home, match.odds_draw, match.odds_guest):
            odds_guest_marker = BashColor.RED
        return odds_home_marker, odds_draw_marker, odds_guest_marker

    def go_to_matchday(self, community, matchday):
        self.browser.get("https://www.kicktipp.de/{community}/tippabgabe?&spieltagIndex={matchday}".format(
            community=community,
            matchday=matchday
        ))

    def retrieve_betting_odds(self):
        matchday_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        match_rows = matchday_page.find('table', id='tippabgabeSpiele').find_all('tr', class_='datarow')

        matches = []

        for match_row in match_rows[1:]:
            match = namedtuple('Match', ['home_team', 'guest_team', 'odds_home', 'odds_draw', 'odds_guest'])
            match.home_team = match_row.find('td', class_='col1').get_text()
            match.guest_team = match_row.find('td', class_='col2').get_text()
            match.odds_home = float(match_row.find_all('td', class_='kicktipp-wettquote')[0].get_text().replace(',', '.'))
            match.odds_draw = float(match_row.find_all('td', class_='kicktipp-wettquote')[1].get_text().replace(',', '.'))
            match.odds_guest = float(match_row.find_all('td', class_='kicktipp-wettquote')[2].get_text().replace(',', '.'))
            matches.append(match)

        return matches

    @staticmethod
    def calculate_tips(matches):
        for match in matches:
            match.tip_home = max(round(math.log((match.odds_guest - 1), 1.75)), 0)
            match.tip_guest = max(round(math.log((match.odds_home - 1), 1.75)), 0)

    def enter_tips(self, matches):
        for i in range(len(matches)):
            match = matches[i]
            match_row = self.browser.find_element_by_id('tippabgabeSpiele').find_elements_by_css_selector('.datarow')[1:][i]
            input_fields = match_row.find_elements_by_tag_name('input')
            if len(input_fields) == 0:
                print("{prefix} could not enter tip for game {index} - no input fields present.".format(
                    prefix=BashColor.BOLD + BashColor.VIOLET + " └──> WARN: " + BashColor.END,
                    index=BashColor.BOLD + str(i+1) + BashColor.END
                ))
                continue
            input_fields[1].clear()
            input_fields[1].send_keys(match.tip_home)
            input_fields[2].clear()
            input_fields[2].send_keys(match.tip_guest)

        self.browser.find_element_by_xpath("//form[@id='tippabgabeForm']//input[@type='submit']").click()
