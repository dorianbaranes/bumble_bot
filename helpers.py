import subprocess
from appium.webdriver.extensions.android.nativekey import AndroidKey
import time
from appium.webdriver.common.touch_action import TouchAction
import logging_config

logger = logging_config.setup_logger(__name__)

ANDROID_KEYCODE_MAP = None




def is_internet_available(driver):
    device_id = driver.capabilities['deviceUDID']
    adb_command = ["adb", "-s", device_id, "shell", "ping","-c","1","google.com"]
    try:
        subprocess.check_output(adb_command, universal_newlines=True)
        return True
    except:
        return False


def close_app(package_name):
    try:
        logger.info(f'Close app {package_name}')
        subprocess.check_output(["adb", "shell","am","force-stop",package_name], universal_newlines=True)
    except:
        logger.info('Can not restart adb server')

def restart_adb_server():
    try:
        logger.info('Restart adb server')
        subprocess.check_output(["adb", "kill-server"], universal_newlines=True)
        subprocess.check_output(["adb", "start-server"], universal_newlines=True)
        time.sleep(5)
    except:
        logger.info('Can not restart adb server')

def get_current_activity_name():
    try:
        adb_cmd="adb shell dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8"
        return str(subprocess.check_output(adb_cmd, shell=True))
    except:
        return None



def generate_android_key_map():
    global ANDROID_KEYCODE_MAP
    ANDROID_KEYCODE_MAP = AndroidKey.__dict__
    special_char = {
        " ": 62,
        ".": 56,
        ",": 55,
        "!": 33,
        "?": 34,
        "@": 77,
        "#": 18,
        "$": 19,
        "%": 20,
        "^": 161,
        "&": 150,
        "*": 17,
        "(": 162,
        ")": 163,
        "-": 69,
        "_": 173,
        "=": 70,
        "+": 81,
        "[": 71,
        "]": 72,
        "{": 87,
        "}": 88,
        "\\": 73,
        "|": 74,
        ";": 39,
        ":": 74,
        "'": 75,
        '"': 76,
        "/": 76,
        "<": 179,
        ">": 180,
        "`": 68,
        "~": 131,
    }
    ANDROID_KEYCODE_MAP = {**AndroidKey.__dict__, **special_char}

#very slow
def insert_text_with_typing(driver, text):
        for char in text:
            if char.isupper():
                driver.press_keycode(
                    keycode=ANDROID_KEYCODE_MAP[char], metastate=1, flags=None
                )
            elif char.islower():
                driver.press_keycode(
                    keycode=ANDROID_KEYCODE_MAP[char.upper()],
                    metastate=None,
                    flags=None,
                )
            elif char.isdigit():
                driver.press_keycode(
                    keycode=ANDROID_KEYCODE_MAP[f"DIGIT_{char}"],
                    metastate=None,
                    flags=None,
                )
            elif char in ANDROID_KEYCODE_MAP.keys():
                driver.press_keycode(
                    keycode=ANDROID_KEYCODE_MAP[char], metastate=None, flags=None
                )
            else:
                logger.info(f"Can write that char:{char}")

def insert_text(driver, text):
        device_id = driver.capabilities['deviceUDID']


        # print each part using a loop
        parts=text.split(' ')
        for part_index in range(len(parts)):
            if part_index == 0:
                word = parts[part_index]+' '+parts[part_index+1][0]
            elif part_index!=len(parts)-1:
                word=parts[part_index][1:]+' '+parts[part_index+1][0]
            else:
                word = parts[part_index][1:]

            if word=='':
                continue


            if "'" in word or '"' in word:
                insert_text_with_typing(driver,word)
                continue
            adb_command = ["adb", "-s",device_id, "shell", "input", "text", word.replace(' ','\ ')]
            # run the ADB command and capture the output
            subprocess.check_output(adb_command, universal_newlines=True)
            time.sleep(1)

def scroll_down(driver):
        # Get the dimensions of the device screen
        screen_width = driver.get_window_size()["width"]
        screen_height = driver.get_window_size()["height"]
        x_start = int(screen_width * 0.5)
        y_start = int(screen_height * 0.7)
        y_end = int(screen_width * 0.5)
        driver.swipe(x_start, y_start, x_start, y_end, 2000)

def scroll_up(driver):
        # Get the dimensions of the device screen
        screen_width = driver.get_window_size()["width"]
        screen_height = driver.get_window_size()["height"]
        x_start = int(screen_width * 0.5)
        y_start = int(screen_height * 0.5)
        y_end = int(screen_width * 0.8)
        driver.swipe(x_start, y_start, x_start, y_end, 2000)

def tap_in_middle_screen(driver):
        screen_width = driver.get_window_size()["width"]
        screen_height = driver.get_window_size()["height"]
        touch = TouchAction(driver)
        touch.tap(x=int(screen_width * 0.5), y=int(screen_height * 0.3)).perform()