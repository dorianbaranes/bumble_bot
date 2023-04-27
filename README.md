Sure, here's a sample README file for your project:

# Bumble Bot

This project automates swiping and messaging on the Bumble app using Appium.

## Requirements

- Python 3.6 or later
- Appium and dependancies (https://appium.io/docs/en/2.0/quickstart/install/)
- An Android emulator or Android phone connected to your computer
- The Bumble app installed on your emulator or phone

## Installation

1. Clone the repository: `git clone https://github.com/your_username/bumble-swiper.git`
2. Navigate to the project directory: `cd bumble-swiper`
3. Install the required packages: `pip install -r requirements.txt`
4. Edit the `SETTINGS.json` file to your liking (see below)
5. From Android phone go to: Settings > Developer options and activate "Don't lock screen"
6. Run the script: `python main.py`

## `SETTINGS.json` fields
- `DEVICE_NAME` (integer): Device ID where to run the script (To get your name: `adb devices`)
- `NB_SWIPES_MIN` (integer): The minimum number of swipes to perform per session
- `NB_SWIPES_MAX` (integer): The maximum number of swipes to perform per session
- `PERCENT_TO_SWIPE_RIGHT` (integer): The percentage of right-swiping (0-100)
- `PERCENT_TO_MESSAGE_AFTER_MATCHING` (integer): The percentage of matches to message (0-100)
- `MESSAGES_INTRO` (list of strings): The list of introduction messages to send
- `NB_SESSION_PER_DAY` (integer): The number of sessions to perform per day
- `BIOS` (list of strings): The list of biographies 
- `BIOS_BLACKLISTED` (list of strings): The list of biographies blacklisted by Bumble
- `BIOS_CURRENT` (dictionary): The current biography for each Bumble app package
- `APP_PACKAGES` (list of strings): The list of Bumble app package names

## Usage

The script runs indefinitely until it reaches the maximum number of sessions per day. You can stop the script manually by pressing `Ctrl+C`.
<br><br>The script is composed in two stages. First stage it checks on all account that the biography is still remaining. <br>
Second it swipe and send messages randomly based on the settings file.
## Troubleshooting

If you encounter any issues while running the script, please check the log file (`app.log`) for more information. You can also consult the Appium documentation for more information on how to use the Appium library.