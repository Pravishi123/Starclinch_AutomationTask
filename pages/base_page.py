"""Common Selenium behavior shared by every page object."""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

from config.config import EXPLICIT_WAIT_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT_SECONDS)

    def open(self, url: str):
        logger.info("Navigating to %s", url)
        self.driver.get(url)

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_all_visible(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def wait_present(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_invisible(self, locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_url_contains(self, fragment: str):
        return self.wait.until(EC.url_contains(fragment))

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def click(self, locator):
        """A handful of CTAs on this site can be intercepted by the sticky top promo
        bar or another absolutely-positioned overlay depending on scroll position, even
        after scrollIntoView. Native click is attempted first since it best represents
        a real user; a JS click is used as a logged fallback rather than hiding the
        retry - see docs/test_execution_summary.md."""
        element = self.wait_clickable(locator)
        self.scroll_into_view(element)
        try:
            element.click()
        except ElementClickInterceptedException:
            logger.warning("Native click intercepted on %s - falling back to JS click", locator)
            self.driver.execute_script("arguments[0].click();", element)
        return element

    def js_click(self, locator):
        """Click via JS instead of a native click. Reserved for the duration/budget-tier
        tiles, whose custom circular layout causes native-click coordinate resolution to
        land on an overlapping sibling; a JS click dispatches directly on the element
        itself instead of at computed screen coordinates."""
        element = self.wait_present(locator)
        self.scroll_into_view(element)
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def type_text(self, locator, text: str, clear_first: bool = True):
        element = self.wait_visible(locator)
        self.scroll_into_view(element)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return element

    def get_text(self, locator) -> str:
        return self.wait_visible(locator).text.strip()

    def is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def find(self, locator):
        return self.wait_present(locator)

    def find_all(self, locator):
        return self.driver.find_elements(*locator)
