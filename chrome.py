import unittest
import time
import json
from pathlib import Path
from selenium import webdriver

ad_block_extension = '/home/laurabarluzzi/Downloads/AdBlock_v3.41.0.crx'
ad_block_installed_title = "AdBlock is now installed!"

WEBSITES_PATH = Path(__file__).parent / 'websites.json'
SCREENSHOTS_PATH = Path(__file__).parent / 'screenshots'

with WEBSITES_PATH.open('r', encoding='utf-8') as fobj:
    URLS = json.load(fobj)


class WebsiteWithExtension(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.urls = URLS
        cls.options = webdriver.ChromeOptions()
        cls.options.add_extension(ad_block_extension)
        cls.options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(options=cls.options)
        cls.setup_timestamp = time.time()
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": cls.setup_timestamp
        }
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platform", "platform_name").lower()
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name").lower(),
                                 cls.driver.capabilities.get("version", 0)))
        cls.log_file = cls.directory / "logs.json"
        _assure_directories_exist(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.metadata["test_end_timestamp"] = time.time()
        try:
            with cls.log_file.open('r', encoding='utf-8') as log_file:
                logs = json.load(log_file)
        except FileNotFoundError:
            logs = []

        logs.append(cls.metadata)

        with cls.log_file.open('w', encoding='utf-8') as log_file:
            json.dump(logs, log_file)

    def test_extension_installed(self):
        driver = self.driver
        self._wait_for_condition(lambda: driver.title == ad_block_installed_title)

    def test_search_in_python_org(self):
        for url in self.urls:
            index = self.urls.index(url)
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_with.png".format(index)).lower()
            self.driver.execute_script("""
                document.body.style.transform='scale(.5)';
                document.body.style.transformOrigin = 'top center';
            """)
            time.sleep(0.5)
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
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(options=cls.options)
        cls.setup_timestamp = time.time()
        cls.metadata = {
            "browser_and_system_info": cls.driver.capabilities,
            "browser_window_size": (1080, 2048),
            "test_start_timestamp": cls.setup_timestamp
        }
        cls.directory = (
                SCREENSHOTS_PATH
                / cls.driver.capabilities.get("platform", "platform_name").lower()
                / "{}_{}".format(cls.driver.capabilities.get("browserName", "browser_name"),
                                 cls.driver.capabilities.get("version", 0)))
        cls.log_file = cls.directory / "logs.json"
        _assure_directories_exist(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.metadata["test_end_timestamp"] = time.time()
        try:
            with cls.log_file.open('r', encoding='utf-8') as log_file:
                logs = json.load(log_file)
        except FileNotFoundError:
            logs = []

        logs.append(cls.metadata)

        with cls.log_file.open('w', encoding='utf-8') as log_file:
            json.dump(logs, log_file)

    def test_search_in_python_org(self):
        for url in self.urls:
            index = self.urls.index(url)
            self.driver.get(url)
            time.sleep(1)
            path_to_screenshot = str(self.directory / "{}_without.png".format(index)).lower()
            self.driver.execute_script("""
                document.body.style.transform='scale(.5)';
                document.body.style.transformOrigin = 'top center';
            """)
            time.sleep(5)
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
