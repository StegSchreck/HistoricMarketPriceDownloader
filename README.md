# Historic Market Price Downloader

<p align="center">
  <img src="https://raw.githubusercontent.com/StegSchreck/HistoricMarketPriceDownloader/master/HistoricMarketPriceDownloader.png" width="400px">
</p>

This project serves as an automated way to download all available historic market prices of a stock from [ariva.de](https://www.ariva.de/) and saves them as a JSON file. This JSON file can then be used for uploading it to [PortfolioPerformance](https://www.portfolio-performance.info/en/).


## Preconditions
1. Make sure you have Python3, Firefox and Xvfb installed on your system. This project is designed to run on Linux.
1. Checkout the project
    `git clone https://github.com/StegSchreck/HistoricMarketPriceDownloader.git && cd HistoricMarketPriceDownloader`
1. Install the requirements with pip for Python3
    `pip3 install -r requirements.txt`
1. Install Geckodriver

      * Use your system's package manager (if it contains Geckodriver)
        * Arch Linux: `pacman -S geckodriver`
        * MacOS: `brew install geckodriver`
      * Or execute `sudo ./InstallGeckodriver.sh`.
        For this you will need to have tar and wget installed.


## Running the script
After ensuring that you met the preconditions, you can simply run the following command in your terminal using the ISIN of the stock you want to parse:
```
python3 main.py --isin <isin>
```


## Call arguments / parameters
### Mandatory
`-i` / `--isin`: ISIN of the stock

### Optional
`-m` / `--market_place`: Name of the marketplace to use. If given marketplace is not available, the default selection on the site is used.

`-d` / `--destination`: destination folder for the resulting CSV file containing the parsed data - independent from `-f`/`--filename`

`-f` / `--filename`: filename for the result CSV - independent from `-d`/`--destination`

`-v` / `--verbose`: increase output verbosity (i.e. print the generated predictions in the console)

`-x` / `--show_browser`: show the browser doing his work (this might help for debugging)

`-h` / `--help`: Display the help, including all possible parameter options


## Troubleshooting
### Script aborts with `ElementClickInterceptedException`
This happens because an advertisement is obscuring the button to click for saving the predictions.
```
selenium.common.exceptions.ElementClickInterceptedException: Message: Element <input name="submitbutton" type="submit"> is not clickable at point (354,523.0666656494141) because another element <iframe id="google_ads_iframe_/39752343/leaderboard_1_0" name="" src="https://tpc.googlesyndication.com/safeframe/1-0-29/html/container.html"> obscures it
```
If you experience this, we can recommend using the `-x` option, which will display the Firefox browser doing the action.

### Script aborts with `WebDriverException`
If you recently updated your Firefox, you might encounter the following exception during the login attempt of the parser:
```
selenium.common.exceptions.WebDriverException: Message: Expected [object Undefined] undefined to be a string
```

This can be fixed by installing the latest version of [Mozilla's Geckodriver](https://github.com/mozilla/geckodriver)
by running again the _Install Geckodriver_ command mentioned [above](#preconditions).
