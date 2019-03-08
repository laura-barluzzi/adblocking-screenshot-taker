#chromedriver_version := $(shell google-chrome --version | cut -d' ' -f3)
chromedriver_version := 72.0.3626.69
geckodriver_version := v0.24.0

port := 8080
env := env
os := $(shell uname | sed 's/Darwin/macos/' | sed 's/Linux/linux64/')

demo: run_firefox run_chrome
	python3 -m http.server $(port)

$(env)/pip-install.done: requirements.txt
	@if [ ! -d "$(env)" ]; then python3 -m venv "$(env)" && "$(env)/bin/pip" install -U pip wheel; fi
	@"$(env)/bin/pip" install -r requirements.txt | tee "$(env)/pip-install.done"

#
# Chrome section
#

$(env)/drivers/chrome/$(chromedriver_version)/chromedriver:
	@mkdir -p "$(env)/drivers/chrome/$(chromedriver_version)/"
	@if ! curl -fSsL "https://chromedriver.storage.googleapis.com/$(chromedriver_version)/chromedriver_linux64.zip" > "$(env)/drivers/chrome/$(chromedriver_version)/chromedriver.zip"; then \
    echo "================================================================================="; \
    echo "Chromedriver version '$(chromedriver_version)' does not exist."; \
    echo "Find available versions here: https://chromedriver.storage.googleapis.com" ; \
    echo "Run make run_chrome -e chromedriver_version=xxx where xxx is the version number."; \
    echo "================================================================================="; \
    exit 1; \
  fi
	@unzip "$(env)/drivers/chrome/$(chromedriver_version)/chromedriver.zip" -d "$(env)/drivers/chrome/$(chromedriver_version)/"

run_chrome: $(env)/pip-install.done $(env)/drivers/chrome/$(chromedriver_version)/chromedriver
	@PATH="$(env)/drivers/chrome/$(chromedriver_version):$(PATH)" "$(env)/bin/python" chrome.py

#
# Firefox section
#

$(env)/drivers/firefox/$(os)/geckodriver:
	@mkdir -p "$(env)/drivers/firefox/$(os)/"
	@curl -fs https://api.github.com/repos/mozilla/geckodriver/releases/latest |\
  python3 -c "import json, sys; print(next(asset['browser_download_url'] for asset in json.load(sys.stdin)['assets'] if '$(os)' in asset['name']))" |\
  xargs -I url curl -fSsL url > "$(env)/drivers/firefox/$(os)/geckodriver.tar.gz"
	@tar -xzf "$(env)/drivers/firefox/$(os)/geckodriver.tar.gz" -C "$(env)/drivers/firefox/$(os)/"
	@chmod +x "$(env)/drivers/firefox/$(os)/geckodriver"

run_firefox: $(env)/pip-install.done $(env)/drivers/firefox/$(os)/geckodriver
	@PATH="$(env)/drivers/firefox/$(os):$(PATH)" "$(env)/bin/python" firefox.py
