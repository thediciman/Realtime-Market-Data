from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep
from os import system
import re

class ConfigReader:

    def __init__(self, filename):
        self.__config_values = {}
        self.__init_configs(filename)

    def __init_configs(self, filename):
        with open(filename, 'r') as config_file:
            while line := config_file.readline():
                line = line.strip()

                if len(line) == 0:
                    continue

                if line[0] == '#':
                    continue

                key_value = line.split('=', 1)

                if len(key_value) != 2:
                    print(f'possibly invalid line: "{line}"')
                    continue

                key_value = list(map(lambda x : x.strip(), key_value))

                key, value = key_value

                self.__config_values[key] = value

    def __getitem__(self, key):
        if key in self.__config_values:
            return self.__config_values[key]

        raise Exception(f'key {key} not found in config')

    def get_or_default(self, key, default = None):
        if key in self.__config_values:
            return self.__config_values[key]
        
        return default

def printPL(data):

    processed_data = {}

    for d in data:
        processed_data[d['ticker']] = float(d['price'])

    print()

    two_decimals_float_format = '{:.2f}'

    transactions = [
        {
            'ticker': 'GME',
            'paid': 420.00,
            'buy': 69.00,
        },
    ]
 
    total_profit_loss = 0.0
    one_usd_to_ron = 4.05

    for transaction in transactions:
        ticker = transaction['ticker']
        profit_loss = (processed_data[ticker] / transaction['buy'] - 1) * transaction['paid']
        percent_change = (processed_data[ticker] / transaction['buy'] - 1) * 100
        total_profit_loss += profit_loss

        print(f"P/L for {transaction['ticker']}: {two_decimals_float_format.format(profit_loss)} USD ( {two_decimals_float_format.format(profit_loss * one_usd_to_ron)} RON ) [ {two_decimals_float_format.format(percent_change)}% ]")

    print()
    print(f"Total P/L: {two_decimals_float_format.format(total_profit_loss)} USD ( {two_decimals_float_format.format(total_profit_loss * one_usd_to_ron)} RON )")
    print()

    total_portfolio_value = total_profit_loss
    total_investments = 0.0

    for transaction in transactions:
        total_investments += transaction['paid']

    total_portfolio_value += total_investments

    portfolio_percent_change = (total_portfolio_value / total_investments - 1) * 100

    print(f"Total portfolio value: {two_decimals_float_format.format(total_portfolio_value)} USD ( {two_decimals_float_format.format(total_portfolio_value * one_usd_to_ron)} RON ) [ {two_decimals_float_format.format(portfolio_percent_change)}% ]")
    print()


if __name__ == '__main__':

    config_reader = ConfigReader('app.properties')
    
    PROFILE_PATH = config_reader['chrome_profile_path']

    prefs = {}

    prefs["download.default_directory"] = "."
    prefs["download.prompt_for_download"] = False
    prefs["download.extensions_to_open"] = "js"
    prefs["safebrowsing.enabled"] = True

    options = Options()
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--safebrowsing-disable-download-protection")
    options.add_argument("safebrowsing-disable-extension-blacklist")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument(f"user-data-dir={PROFILE_PATH}")

    driver = webdriver.Chrome("./chromedriver", chrome_options=options)

    prices = []

    ticker = config_reader['ticker']
    driver.get(f"https://finance.yahoo.com/quote/{ticker}?p={ticker}")

    while True:

        system('cls')

        for p in prices:
            print(f"{p['ticker']} price: {p['price']}")

        try:
            printPL(prices)
        except Exception as ex:
            print(ex)

        prices = []

        try:
            html_source = str(driver.page_source)

            regex_premarket = 'data-reactid="37">[0-9]*\.[0-9]*</span>'
            regex_actual    = 'data-reactid="32">[0-9]*\.[0-9]*</span>'

            got_price = False

            try:
                price = re.findall(regex_premarket, html_source)[0][18:-7]
                prices.append({'ticker': ticker, 'price': price})
                got_price = True
            except:
                pass

            if got_price == False:
                try:
                    price = re.findall(regex_actual, html_source)[0][18:-7]
                    prices.append({'ticker': ticker, 'price': price})
                except:
                    pass

        except Exception as ex:
            print(ex)
    
        sleep(0.25)