from appium import webdriver
from appium.webdriver.appium_service import AppiumService
import logging_config
from helpers import close_app

logger = logging_config.setup_logger(__name__)


class AppiumServer:
    server = None

    @classmethod
    def start(cls):
        logger.debug(f"Start Appium Server")
        cls.server = AppiumService()
        cls.server.start()

    @classmethod
    def stop(cls):
        logger.debug(f"Stop Appium Server")
        if cls.server:
            cls.server.stop()
            cls.server = None


class AppiumDriverController:
    def __init__(self, device_name, package_name):
        self.device_name = device_name
        self.package_name = package_name
        self._driver = None


    def start(self):
        logger.debug(f"Start Appium Driver")
        capabilities = dict(
            platformName="Android",
            automationName="uiautomator2",
            deviceName=self.device_name,
            appPackage=self.package_name,
            appActivity=".ui.launcher.BumbleLauncherActivity",
            noReset=True,
        )
        appium_server_url = "http://localhost:4723"
        try:
            self._driver = webdriver.Remote(appium_server_url, capabilities)
            self._driver.implicitly_wait(5)
        except Exception as e:
            logger.exception("Failed to start Appium Driver: %s", e)

    def stop(self):
        logger.debug(f"Stop Appium Driver")
        try:
            if self._driver:
                self._driver.terminate_app(self.package_name)
                self._driver.quit()
                self._driver = None
        except Exception as e:
            logger.exception("Failed to stop Appium Driver: %s", e)

    def get_driver(self):
        return self._driver

