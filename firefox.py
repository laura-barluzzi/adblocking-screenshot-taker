import unittest
import time
import platform
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

ad_block_extension = '/home/laurabarluzzi/Downloads/adblock-3.16.2-an+fx.xpi'
ad_block_installed_title = "AdBlock is now installed!"

OS = platform.system()

WEBSITES_PATH = Path(__file__).parent / 'websites.json'
SCREENSHOTS_PATH = Path(__file__).parent / 'screenshots'

with WEBSITES_PATH.open('r', encoding='utf-8') as fobj:
    URLS = json.load(fobj)


class WebsiteWithExtension(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.urls = URLS
        cls.options = Options()
        cls.options.headless = True
        cls.driver = webdriver.Firefox(options=cls.options)
        cls.driver.set_window_size(1080, 2048)
        cls.driver.install_addon(ad_block_extension, temporary=True)
        cls.setup_timestamp = time.time()
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": cls.setup_timestamp
        }
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platformName", "platform_name")
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name"),
                                 cls.driver.capabilities.get("browserVersion", 0)))
        cls.log_file = cls.directory / "logs.json"
        _assure_directories_exist(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.metadata["test_end_timestamp"] = time.time()
        with cls.log_file.open('a+', encoding='utf-8') as log_file:
            json.dump(cls.metadata, log_file)

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

    def test_search_in_python_org(self):
        for url in self.urls:
            index = self.urls.index(url)
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_with.png".format(index))
            self.driver.save_screenshot(path_to_screenshot)

            page_title = self.driver.title
            page_url = self.driver.current_url
            timestamp = time.time()
            this_page_metadata = {
                "url": page_url,
                "title": page_title,
                "timestamp": timestamp,
                "path_to_screenshot": path_to_screenshot
            }
            self.metadata[index] = this_page_metadata

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
        cls.driver = webdriver.Firefox(timeout=50, options=cls.options)
        cls.driver.set_window_size(1080, 2048)
        cls.setup_timestamp = time.time()
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": cls.setup_timestamp
        }
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platformName", "platform_name")
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name"),
                                 cls.driver.capabilities.get("browserVersion", 0)))
        cls.log_file = cls.directory / "logs.json"
        _assure_directories_exist(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.metadata["test_end_timestamp"] = time.time()
        with cls.log_file.open('a+', encoding='utf-8') as log_file:
            json.dump(cls.metadata, log_file)

    def test_search_in_python_org(self):
        for url in self.urls:
            index = self.urls.index(url)
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_without.png".format(index))
            self.driver.get_screenshot_as_file(path_to_screenshot)

            page_title = self.driver.title
            page_url = self.driver.current_url
            timestamp = time.time()
            this_page_metadata = {
                "url": page_url,
                "title": page_title,
                "timestamp": timestamp,
                "path_to_screenshot": path_to_screenshot
            }
            self.metadata[index] = this_page_metadata


def _assure_directories_exist(path):
    Path(path).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    unittest.main()
