import unittest
import time
import json
import utils as u
from shutil import copyfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

ad_block_extension = '/home/laurabarluzzi/Downloads/adblock-3.16.2-an+fx.xpi'
ad_block_installed_title = "AdBlock is now installed!"
START_TIME = time.ctime().replace(' ', '_').replace(':', '_')

WEBSITES_PATH = Path(__file__).parent / 'websites.json'
SCREENSHOTS_PATH = Path(__file__).parent / 'screenshots' / START_TIME
SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

copyfile(Path(__file__).parent / 'index.html', SCREENSHOTS_PATH / 'index.html')

with WEBSITES_PATH.open('r', encoding='utf-8') as fobj:
    URLS = json.load(fobj)


class WebsiteWithExtension(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.urls = URLS
        cls.options = Options()
        cls.options.headless = True
        cls.options.set_preference("media.volume_scale", "0.0")
        cls.driver = webdriver.Firefox(options=cls.options)
        cls.driver.set_window_size(1080, 2048)
        cls.driver.install_addon(ad_block_extension, temporary=True)
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": time.time()
        }
        cls.extension_status = "with_extension"
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platformName", "platform_name").lower()
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name"),
                                 cls.driver.capabilities.get("browserVersion", 0)))
        cls.log_file = cls.directory / "logs.json"
        u._assure_directories_exist(cls.directory)
        u._add_metatdata(cls.log_file, cls.metadata)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_extension_installed(self):
        driver = self.driver

        about_blank_tab = driver.current_window_handle
        self.assertEqual(driver.title, "")
        self._wait_for_condition(lambda: len(driver.window_handles) == 2)

        adblock_tab = driver.window_handles[1]
        driver.switch_to.window(adblock_tab)
        self._wait_for_condition(lambda: driver.title == ad_block_installed_title)

        driver.close()
        driver.switch_to.window(about_blank_tab)

    def test_websites_with_extension(self):
        for index, url in enumerate(self.urls):
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_{}.png".format(index, self.extension_status))
            self.driver.save_screenshot(path_to_screenshot)

            page_title = self.driver.title
            page_url = self.driver.current_url
            timestamp = time.time()
            this_page_metadata = {
                "url": page_url,
                "title": page_title,
                "timestamp": timestamp,
                "path_to_screenshot": path_to_screenshot,
                "extension_status": self.extension_status
            }
            u._add_url_to_logs(self.log_file, this_page_metadata)

    def _wait_for_condition(self, condition, at_most_sleep=20, sleep_interval=2):
        total_sleep = 0

        while not condition():
            time.sleep(sleep_interval)
            total_sleep += sleep_interval
            if total_sleep >= at_most_sleep:
                self.fail("Condition was not met after {} seconds"
                          .format(at_most_sleep))


class WebsiteWithoutExtension(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.urls = URLS
        cls.options = Options()
        cls.options.headless = True
        cls.options.set_preference("media.volume_scale", "0.0")
        cls.driver = webdriver.Firefox(options=cls.options)
        cls.driver.set_window_size(1080, 2048)
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": time.time()
        }
        cls.extension_status = "without_extension"
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platformName", "platform_name").lower()
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name"),
                                 cls.driver.capabilities.get("browserVersion", 0)))
        cls.log_file = cls.directory / "logs.json"
        u._assure_directories_exist(cls.directory)
        u._add_metatdata(cls.log_file, cls.metadata)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_websites_without_extension(self):
        for index, url in enumerate(self.urls):
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_{}.png".format(index, self.extension_status))
            self.driver.get_screenshot_as_file(path_to_screenshot)

            page_title = self.driver.title
            page_url = self.driver.current_url
            timestamp = time.time()
            this_page_metadata = {
                "url": page_url,
                "title": page_title,
                "timestamp": timestamp,
                "path_to_screenshot": path_to_screenshot,
                "extension_status": self.extension_status
            }
            u._add_url_to_logs(self.log_file, this_page_metadata)


if __name__ == "__main__":
    unittest.main()
