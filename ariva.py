import sys
import time
import urllib.parse
from datetime import datetime
from typing import Optional, List, Dict

from bs4 import BeautifulSoup
from progressbar import ProgressBar
from selenium.common.exceptions import NoSuchElementException

from bash_color import BashColor
from browser_handler import BrowserHandler


class Ariva:
    def __init__(self, args):
        self.args = args

        login_form_selector = "//form[@id='user_login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='ISID']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='ISKW']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"

        self._init_browser()
        self.base_url = f"https://www.ariva.de/"
        self.isin = None
        self.selected_market_id = None
        self.progress_bar = None
        self.market_prices = dict()

    def _init_browser(self):
        self.browser_handler = BrowserHandler(self.args)
        self.browser = self.browser_handler.browser
        self.login()

    def login(self):
        self.browser.get("https://www.ariva.de/user/login")
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

    def _handle_cookie_notice_if_present(self):
        cookie_notice_agree_buttons = self.browser.find_elements_by_xpath(
            "//*[@id='notice']//button"
        )
        if len(cookie_notice_agree_buttons) == 0:
            return
        cookie_notice_agree_button = cookie_notice_agree_buttons[-1]
        if cookie_notice_agree_button is not None:
            cookie_notice_agree_button.click()
            time.sleep(1)

    def print_progress(self, counter: int, historic_period: str, historic_periods: List[str]):
        historic_period_index = historic_periods.index(historic_period) + 1
        if self.args and self.args.verbose and self.args.verbose >= 1:
            print(f"{self.isin}: [{historic_period_index}/{len(historic_periods)}] parsing {historic_period}")
        else:
            self._print_progress_bar(counter, historic_periods)

    def _print_progress_bar(self, counter: int, historic_periods: List[str]):
        if not self.progress_bar:
            self.progress_bar = ProgressBar(max_value=len(historic_periods), redirect_stdout=True)
        self.progress_bar.update(counter)
        if counter == len(historic_periods):
            self.progress_bar.finish()

    def download(self, isin: str, market_place: Optional[str]) -> Dict[str, str]:
        self.isin = isin
        self.base_url = f"https://www.ariva.de/{self.isin}/kurse/historische-kurse"
        self.go_to_stock_page()

        stock_page = BeautifulSoup(self.browser.page_source, "html.parser")
        stock_name = stock_page.find("h1").get_text().replace("Historische Kurse", '').strip()
        print(f"{BashColor.BOLD + BashColor.BLUE}INFO:{BashColor.END} Parsing [{self.isin}] {stock_name}")

        self.select_market_place(market_place)
        self.parse_stock_market_prices()
        return self.market_prices

    def go_to_stock_page(self, selected_historic_period: Optional[str] = None):
        url_to_visit = self.base_url
        if self.selected_market_id or selected_historic_period:
            url_to_visit += "?"
        if self.selected_market_id:
            url_to_visit += urllib.parse.urlencode({"boerse_id": self.selected_market_id})
        if self.selected_market_id and selected_historic_period:
            url_to_visit += "&"
        if selected_historic_period:
            url_to_visit += urllib.parse.urlencode({"month": selected_historic_period})
        self.browser.get(url_to_visit)
        time.sleep(0.5)

    def select_market_place(self, market_place: Optional[str]):
        stock_page = BeautifulSoup(self.browser.page_source, "html.parser")
        market_place_select = stock_page.find(class_='handelsplatz')
        market_place_options = market_place_select.find_all('option')
        preselected_market_place_option = market_place_select.find('option', selected=True)
        available_market_places = dict()
        for market_place_option in market_place_options:
            available_market_places[market_place_option.get_text().upper()] = market_place_option["value"]

        if market_place and market_place.upper() in available_market_places.keys():
            self.selected_market_id = available_market_places.get(market_place.upper())
        elif market_place:
            self.selected_market_id = preselected_market_place_option
            print(f"{BashColor.BOLD + BashColor.BLUE} └──> INFO: {BashColor.END}"
                  f"No market place chosen. Using default value {preselected_market_place_option.get_text()}")
        else:
            self.selected_market_id = preselected_market_place_option
            print(f"{BashColor.BOLD + BashColor.YELLOW} └──> WARN: {BashColor.END}"
                  f"Requested market place {market_place} not available. "
                  f"Using default value {preselected_market_place_option.get_text()}")

        self.go_to_stock_page()

    def parse_stock_market_prices(self):
        stock_page = BeautifulSoup(self.browser.page_source, "html.parser")
        historic_period_select = stock_page.find("select", attrs={"name": "month"})
        historic_period_options = historic_period_select.find_all('option')
        historic_period_values = [option['value'] for option in historic_period_options if option['value']]

        for i in range(len(historic_period_values)):
            historic_period_to_parse = historic_period_values[i]
            self.print_progress(i+1, historic_period_to_parse, historic_period_values)
            self.go_to_stock_page(historic_period_to_parse)
            self.parse_stock_market_prices_for_period()

    def parse_stock_market_prices_for_period(self):
        stock_page = BeautifulSoup(self.browser.page_source, "html.parser")
        price_table_rows = stock_page.find(id='pageHistoricQuotes').find("table", class_="line").find_all('tr', class_="arrow0")

        if self.args and self.args.verbose and self.args.verbose >= 2:
            print(f"parsing {len(price_table_rows)} table rows")
        for price_table_row in price_table_rows:
            market_price_date = datetime.strptime(price_table_row.find_all('td')[0].get_text(), '%d.%m.%y').strftime('%Y-%m-%d').strip()
            market_price_value = price_table_row.find_all('td')[3].get_text().replace('.', '').strip()  # entries are using comma as decimal separator
            self.market_prices[market_price_date] = market_price_value
            if self.args and self.args.verbose and self.args.verbose >= 2:
                print(f"{self.isin}: [{market_price_date}] {market_price_value}")

