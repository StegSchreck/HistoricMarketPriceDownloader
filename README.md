# Kicktipper

<p align="center">
  <img src="https://raw.githubusercontent.com/WiSchLabs/Kicktipper/master/Kicktipper.png" width="400px">
</p>

This project serves as an automated way to enter predictions for a [Kicktipp](https://www.kicktipp.de) community.

**NOTE**: This script requires the admin of the prediction community to activate the option to show the betting odds in
the settings menu.


## Preconditions
1. Make sure you have Python3, Firefox and Xvfb installed on your system. This project is designed to run on Linux.
1. Checkout the project
    `git clone https://github.com/WiSchLabs/Kicktipper.git && cd Kicktipper`
1. Install the requirements with pip for Python3
    `pip3 install -r requirements.txt`
1. Install Geckodriver

      * Use your system's package manager (if it contains Geckodriver)
        * Arch Linux: `pacman -S geckodriver`
        * MacOS: `brew install geckodriver`
      * Or execute `sudo ./InstallGeckodriver.sh`.
        For this you will need to have tar and wget installed.


## Running the script
There are multiple modes this script can run with:

### Predictions based on betting odds
By default, this script will use this mode, unless you set a different mode (see below).
```
python main.py -u <your.name@domain.com> -p <your_secret_password> -c <name_of_the_prediction_game> -m 1
```

You can also enter the predictions for multiple matchdays at once by defining another `-m` parameter, e.g.:
```
python main.py -u <your.name@domain.com> -p <your_secret_password> -c <name_of_the_prediction_game> -m 1 -m 2 -m 3
```

### Predictions _against_ betting odds (favor the underdog)
By defining the `-a` or `--anti` parameter, the script will set the prediction to let the underdog win the match
with a result of 1:0.
The "underdog" is defined having the higher number when parsing the betting odds.
```
python main.py -u <your.name@domain.com> -p <your_secret_password> -c <name_of_the_prediction_game> -m 1 -a
```

### Static prediction for every match
By defining the `-s` or `--static` parameter, you can choose to set the same prediction result for every match.
For example, this will set every prediction to 4:2: 
```
python main.py -u <your.name@domain.com> -p <your_secret_password> -c <name_of_the_prediction_game> -m 1 -s 4:2
```

### Random predictions
By defining the `-r` or `--random` parameter, you can choose to set a randomly generated prediction result for every match.
This will randomly choose a number between 0 and 4 for the home team and guest team of the matches independently.
```
python main.py -u <your.name@domain.com> -p <your_secret_password> -c <name_of_the_prediction_game> -m 1 -r
```


## Call arguments / parameters
### Mandatory
`-u` / `--username`: username for Kicktipp login (for the user that should receive the generated predictions)

`-p` / `--password`: password for Kicktipp login

`-c` / `--community`: Kicktipp prediction community

`-m` / `--matchday`: Number of the matchday to enter prediction for.
You can define multiple matchdays to be considered by setting multiple `-m` parameters

By default the script will try to enter the predictions based on betting odds displayed on the page (see above).

### Optional
`-v` / `--verbose`: increase output verbosity (i.e. print the generated predictions in the console)

`-x` / `--show_browser`: show the browser doing his work (this might help for debugging)

`-d` / `--dryrun`: Do not insert into Kicktipp, only print calculated results on console

`-r` / `--random`: Generate random scores and ignore betting odds (see modes above)

`-a` / `--anti`: Generate scores by favoring the underdog according to betting odds (see modes above)

`-s` / `--static`: Generate static scores (see modes above)

`-h` / `--help`: Display the help, including all possible parameter options


## Trouble shooting
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

### Login attempt does not work
This can have multiple explanations.
One is, that you are using a password which starts or ends with a space character.
Kicktipper is currently not capable of dealing with that.
If your credentials have a space character in the middle though, it will work fine. 