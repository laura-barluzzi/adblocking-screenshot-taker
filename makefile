chromedriver_version := $(shell google-chrome --version | cut -d' ' -f3)
env := env

$(env)/pip-install.done: requirements.txt
	if [ ! -d "$(env)" ]; then python3 -m venv "$(env)" && "$(env)/bin/pip" install -U pip wheel; fi
	"$(env)/bin/pip" install -r requirements.txt | tee "$(env)/pip-install.done"

$(env)/drivers/chrome/$(chromedriver_version)/chromedriver:
	mkdir -p "$(env)/drivers/chrome/$(chromedriver_version)/"
	wget "https://chromedriver.storage.googleapis.com/$(chromedriver_version)/chromedriver_linux64.zip" -O "$(env)/drivers/chrome/$(chromedriver_version)/driver.zip"
	unzip "$(env)/drivers/chrome/$(chromedriver_version)/driver.zip" -d "$(env)/drivers/chrome/$(chromedriver_version)/"

run_chrome: $(env)/pip-install.done $(env)/drivers/chrome/$(chromedriver_version)/chromedriver
	PATH="$(env)/drivers/chrome/$(chromedriver_version):$(PATH)" "$(env)/bin/python" chrome.py
