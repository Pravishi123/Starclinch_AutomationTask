"""Creates configured WebDriver instances. Chrome is the primary, verified browser;
Firefox is supported via the same Selenium Manager mechanism but was not verified in the
environment this framework was built in (no local Firefox install) - see README known
limitations."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from utils.logger import get_logger

logger = get_logger(__name__)


def create_driver(browser: str = "chrome", headless: bool = False):
    browser = (browser or "chrome").lower()
    logger.info("Starting %s driver (headless=%s)", browser, headless)

    if browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    if headless:
        driver.set_window_size(1920, 1080)
    driver.implicitly_wait(0)
    return driver
