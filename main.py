import time
import random
import json
import traceback
from enum import Enum
from appium.webdriver.common.appiumby import AppiumBy
from appium_utils import AppiumDriverController, AppiumServer
from helpers import insert_text ,generate_android_key_map, scroll_down,tap_in_middle_screen, restart_adb_server, get_current_activity_name
import logging_config
import sys

logger = logging_config.setup_logger(__name__)

SETTINGS = None

def get_settings():
    logger.info("Read settings")
    global SETTINGS
    with open("SETTINGS.json") as f:
        # Load the JSON data from the file
        SETTINGS = json.load(f)


class SwipeDirection(Enum):
    LEFT = "left"
    RIGHT = "right"

class SessionType(Enum):
    CHECK_BIO = "check biography"
    SWIPING = "do swipping"


class BumbleSession:
    def __init__(self, id, device_name, app_package, nb_swipes, percent_message_after_match=0, percent_swipe_right=0):
        self.device_name= device_name
        self.app_package = app_package
        self.appium_driver_controller = AppiumDriverController(device_name,app_package)
        self.driver = None
        self.nb_swipes = nb_swipes
        self.id=id

        if percent_message_after_match < 0 or percent_message_after_match > 100:
            raise ValueError("Percentage must be between 0 and 100.")
        self.percent_message_after_match= percent_message_after_match
        self.percent_swipe_right=percent_swipe_right

    def should_send_message(self):
        return random.randint(0, 99) < self.percent_message_after_match

    def should_swipe_right(self):
        return random.randint(0, 99) < self.percent_swipe_right


    def swipe(self, direction: SwipeDirection):
        logger.info(f"Swipe to {direction.value}")
        # time.sleep(5)
        logger.info("Search for profile to swipe")
        while True:
            try:
                self.driver.find_element(
                    AppiumBy.ID, f"{self.app_package}:id/discovery_screen_container"
                )
                break
            except:
                self.check_unexpected_events()

        # Get the dimensions of the device screen
        screen_width = self.driver.get_window_size()["width"]
        screen_height = self.driver.get_window_size()["height"]
        y_start = int(screen_height * 0.5)

        if direction == SwipeDirection.LEFT:
            x_start = int(screen_width * 0.6)
            x_end = int(screen_width * 0.0)
        else:
            x_start = int(screen_width * 0.4)
            x_end = int(screen_width * 1.0)

        self.driver.swipe(x_start, y_start, x_end, y_start, 1000)

        try:
            if direction == SwipeDirection.LEFT:
                self.driver.find_element(
                    by=AppiumBy.XPATH, value='//*[@text="NOT INTERESTED"]'
                ).click()
            else:
                self.driver.find_element(
                    by=AppiumBy.XPATH, value='//*[@text="YES"]'
                ).click()
        except:
            pass



    def is_matched(self):
        #Look who's got matches waiting
        try:
            self.driver.implicitly_wait(2)
            self.driver.find_element(
                by=AppiumBy.XPATH, value='//*[@text="Look who\'s got matches waiting"]'
            )  # com.bumble.apr:id/match_explanationTitle
            self.driver.implicitly_wait(5)
            logger.info("Got Popup: Look who\'s got matches waiting ")
            #tap in the middle screen to close bottom modal
            tap_in_middle_screen(self.driver)
        except:
            pass

        try:
            self.driver.find_element(
                by=AppiumBy.XPATH, value='//*[@text="YOU MATCHED!"]'
            )  # com.bumble.apr:id/match_explanationTitle
            logger.info("This is a match")
            return True
        except:
            logger.info("This is not a match")
            return False

    def send_message(self, message):
        logger.debug("click on text field")
        time.sleep(0.5)
        self.driver.find_element(
            AppiumBy.ID, f"{self.app_package}:id/composerMini_text"
        ).click()
        logger.info("type message")
        time.sleep(0.5)
        insert_text(self.driver, message)
        logger.debug("send message")
        time.sleep(0.5)
        self.driver.find_element(
            AppiumBy.ID, f"{self.app_package}:id/composerMini_icon"
        ).click()

    def check_unexpected_events(self):
        event_buttons=[
            "Got it",
        ]

        event_text_buttons=[
            {'text':'Compliment their profile before a match', 'button':'Got it!'},
            {'text': 'Do you enjoy using Bumble?', 'button': 'No'},
            {'text': 'Someone likes you!', 'button': 'Maybe later'},
        ]


        time.sleep(2)
        self.driver.implicitly_wait(0)

        for event_button in event_buttons:
            try:
                self.driver.find_element(
                    by=AppiumBy.XPATH, value=f'//*[@text="{event_button}"]'
                ).click()
            except:
                pass

        for event_text_button in event_text_buttons:
            text=event_text_button['text']
            button=event_text_button['button']
            try:
                self.driver.find_element(
                    by=AppiumBy.XPATH, value=f'//*[@text="{text}"]'
                )
                self.driver.find_element(
                    by=AppiumBy.XPATH, value=f'//*[@text="{button}"]'
                ).click()
            except:
                pass


        try:
            self.driver.find_element(
                by=AppiumBy.XPATH, value='//*[@text="Let Bumble pick a cause"]'
            )
            time.sleep(2)
            self.driver.back()
        except:
            pass

        try:
            self.driver.find_element(
                by=AppiumBy.XPATH, value='//*[@text="You have a new match"]'
            )
            self.driver.back()
        except:
            pass



        while True:
            try:
                self.driver.find_element(
                    by=AppiumBy.XPATH, value='//*[@text="You’re using Bumble offline"]'
                )
                time.sleep(5)
                logger.warning("Internet connection is off")
            except:
                break


        self.driver.implicitly_wait(5)

    def action_check_bio(self):
        logger.info(
            f"Start session BIO Id:{self.id} AppPackage:{self.app_package}"
        )
        self.driver.find_element(
            by=AppiumBy.XPATH, value='//*[@content-desc="Profile"]'
        ).click()


        self.driver.find_element(
            by=AppiumBy.ID, value=f"{self.app_package}:id/menuNavigation_personImageFlipper"
        ).click()

        self.driver.find_element(
            by=AppiumBy.ID, value=f"{self.app_package}:id/myProfilePreview_editProfileButton"
        ).click()

        #scroll down until you see the bio
        while True:
            try:
                bio=self.driver.find_element(
                    by=AppiumBy.ID, value=f"{self.app_package}:id/profile_editor_editable_input"
                )
                scroll_down(self.driver)
                break
            except:
                scroll_down(self.driver)

        bio_value = bio.get_attribute("text")


        if bio_value == 'A little bit about you...':  # the bio has been removed
            logger.info(f'Current Bio is  removed:{SETTINGS["BIOS_CURRENT"][self.app_package]}')
            if SETTINGS['BIOS_CURRENT'][self.app_package]:
                logger.info(f'Bio has been blacklisted:{SETTINGS["BIOS_CURRENT"][self.app_package]}')
                SETTINGS['BIOS_BLACKLISTED'].append(SETTINGS['BIOS_CURRENT'][self.app_package])
                try:
                    SETTINGS["BIOS"].remove(SETTINGS['BIOS_CURRENT'][self.app_package])
                except ValueError:
                    pass


            bio.click()
            new_bio = random.choice(SETTINGS["BIOS"])
            SETTINGS['BIOS_CURRENT'][self.app_package] = new_bio
            insert_text(self.driver, new_bio)
            with open('SETTINGS.json', 'w') as f:
                json.dump(SETTINGS, f, indent=4)

            # valid the update
            self.driver.find_element(
                by=AppiumBy.ID, value=f"{self.app_package}:id/navbar_right_icon_image"
            ).click()
        else:
            logger.info(f'Current Bio is not removed:{bio_value}')


        logger.info(
            f"End session BIO Id:{self.id}"
        )

    def action_do_swiping(self):
        logger.info(
            f"Start session SWIPING Id:{self.id} AppPackage:{self.app_package} with number of swipes:{self.nb_swipes}"
        )
        for i in range(self.nb_swipes):
            logger.info(f"Swipe {i+1}")
            # random_direction = random.choice(list(SwipeDirection))
            random_direction = SwipeDirection.RIGHT if self.should_swipe_right() else SwipeDirection.LEFT
            self.swipe(random_direction)
            try:
                self.driver.find_element(
                    AppiumBy.ID, f"{self.app_package}:id/discovery_screen_container"
                )
                logger.info("This is not a match")
                continue
            except:
                pass


            self.check_unexpected_events()
            if self.is_matched():
                if self.should_send_message():
                    logger.info('Send a random message')
                    random_intro_message = random.choice(SETTINGS["MESSAGES_INTRO"])
                    self.send_message(random_intro_message)
                else:
                    logger.info('Do not send a random message')
                    self.driver.find_element(
                        AppiumBy.ID, f"{self.app_package}:id/match_close"
                    ).click()
            self.check_unexpected_events()
        logger.info(
            f"End session SWIPING Id:{self.id}"
        )


    def launch(self, session_type:SessionType):
        logger.info('---------------------------------------------------')

        try_max=5
        try_nb=1

        while try_nb<=try_max:
            self.appium_driver_controller.start()
            self.driver = self.appium_driver_controller.get_driver()
            time.sleep(5)
            if self.app_package in get_current_activity_name():
                logger.debug("Bumble is launched in screen")
                break

            logger.info(f'Driver did not succeed to launch Bumble (Try:{try_nb})')
            self.appium_driver_controller.stop()
            try_nb+1
            restart_adb_server()

        if try_nb==6:
            logger.error('The driver did not succeed to launch Bumble')
            sys.exit()






        self.check_unexpected_events()
        if session_type==SessionType.SWIPING:
            self.action_do_swiping()
        else:
            self.action_check_bio()

        time.sleep(5)
        self.driver.close_app()
        self.appium_driver_controller.stop()

if __name__ == "__main__":
    get_settings()
    generate_android_key_map()
    restart_adb_server()

    device_name = SETTINGS["DEVICE_NAME"]
    nb_session=SETTINGS["NB_SESSION_PER_DAY"]

    AppiumServer.start()
    #Bio checking
    session_id=1
    for app_package in SETTINGS["APP_PACKAGES"]:
        try:
            nb_swipes = random.randint(SETTINGS["NB_SWIPES_MIN"], SETTINGS["NB_SWIPES_MAX"])
            session = BumbleSession(session_id, device_name, app_package, nb_swipes)
            session.launch(SessionType.CHECK_BIO)
            time.sleep(2)
            session_id+=1
        except Exception as e:
            logger.error(f"Session failed: {e}")
            traceback.print_exc()
            restart_adb_server()

    #Do swipping
    session_id = 1
    for session in range(nb_session):
        try:
            app_package = random.choice(SETTINGS["APP_PACKAGES"])
            nb_swipes = random.randint(SETTINGS["NB_SWIPES_MIN"], SETTINGS["NB_SWIPES_MAX"])
            session = BumbleSession(session_id, device_name, app_package, nb_swipes, SETTINGS["PERCENT_TO_MESSAGE_AFTER_MATCHING"], SETTINGS["PERCENT_TO_SWIPE_RIGHT"])

            session.launch(SessionType.SWIPING)
            time.sleep(2)
            session_id += 1
        except Exception as e:
            logger.error(f"Session failed: {e}")
            traceback.print_exc()
            restart_adb_server()

    AppiumServer.stop()
