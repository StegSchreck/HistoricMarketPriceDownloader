import math
import sys
import time
from collections import namedtuple

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Firefox, DesiredCapabilities, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from xvfbwrapper import Xvfb


class Kicktipp:
    def __init__(self, args):
        self.args = args

        login_form_selector = "//form[@id='loginFormular']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='kennung']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='passwort']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"

        self._init_browser()

    def _init_browser(self):
        if self.args and not self.args.show_browser:
            self.display = Xvfb()
            self.display.start()

        log_level = 'warn'

        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities["moz:firefoxOptions"] = {
            "log": {
                "level": log_level,
            },
        }

        options = Options()
        options.log.level = log_level

        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv, application/zip")
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("devtools.jsonview.enabled", False)
        profile.set_preference("media.volume_scale", "0.0")
        # https://github.com/mozilla/geckodriver/issues/858#issuecomment-322512336
        profile.set_preference("dom.file.createInChild", True)

        self.browser = Firefox(
            firefox_profile=profile,
            capabilities=capabilities,
            firefox_options=options,
            log_path="geckodriver.log"
        )
        # http://stackoverflow.com/questions/42754877/cant-upload-file-using-selenium-with-python-post-post-session-b90ee4c1-ef51-4  # pylint: disable=line-too-long
        self.browser._is_remote = False  # pylint: disable=protected-access

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
            self.kill_browser()
            sys.exit(1)

    def kill_browser(self):
        self.browser.stop_client()
        self.browser.close()
        try:
            self.browser.quit()
        except WebDriverException:
            pass

        if self.args and not self.args.show_browser:
            self.display.stop()

    def handle_matchday(self, matchday):
        self.go_to_matchday(matchday)
        matches = self.retrieve_betting_odds()
        self.calculate_tips(matches)
        self.enter_tips(matches)

    def go_to_matchday(self, matchday):
        self.browser.get("https://www.kicktipp.de/wm-klamauk-referenz/tippabgabe?&spieltagIndex={matchday}".format(
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
            match.odds_home = float(match_row.find('td', class_='col5').get_text().replace(',', '.'))
            match.odds_draw = float(match_row.find('td', class_='col6').get_text().replace(',', '.'))
            match.odds_guest = float(match_row.find('td', class_='col7').get_text().replace(',', '.'))
            matches.append(match)

        return matches

    @staticmethod
    def calculate_tips(matches):
        for match in matches:
            if match.odds_home > match.odds_draw < match.odds_guest:
                match.tip_home = 0
                match.tip_guest = 0
            elif match.odds_home > match.odds_guest:
                match.tip_home = 0
                match.tip_guest = int(round(math.log(match.odds_home - match.odds_guest, 2)))
            else:
                match.tip_home = int(round(math.log(match.odds_guest - match.odds_home, 2)))
                match.tip_guest = 0

    def enter_tips(self, matches):
        for i in range(len(matches)):
            match = matches[i]
            match_row = self.browser.find_element_by_id('tippabgabeSpiele').find_elements_by_css_selector('.datarow')[1:][i]
            match_row.find_elements_by_tag_name('input')[1].clear()
            match_row.find_elements_by_tag_name('input')[1].send_keys(match.tip_home)
            match_row.find_elements_by_tag_name('input')[2].clear()
            match_row.find_elements_by_tag_name('input')[2].send_keys(match.tip_guest)

        self.browser.find_element_by_xpath("//form[@id='tippabgabeForm']//input[@type='submit']").click()
