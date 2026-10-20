"""Step 2 of the real /on-demand wizard: 'Event Details' (event type, date, time,
performing language, and venue/location + serviceability check). Contact fields live
on this same page in the real app; see contact_page.py for those."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class EventDetailsPage(BasePage):
    EVENT_TYPE_BUTTON = (By.CSS_SELECTOR, '[data-field="eventType"] [role="button"]')
    EVENT_DATE_CALENDAR_BUTTON = (By.CSS_SELECTOR, '[data-field="eventDate"] button[aria-label="Open calendar"]')
    EVENT_DATE_INPUT = (By.CSS_SELECTOR, '[data-field="eventDate"] input')
    DATEPICKER_POPPER = (By.CSS_SELECTOR, ".react-datepicker-popper")

    INCREASE_HOUR = (By.CSS_SELECTOR, 'button[aria-label="Increase hour"]')
    DECREASE_HOUR = (By.CSS_SELECTOR, 'button[aria-label="Decrease hour"]')
    INCREASE_MINUTE = (By.CSS_SELECTOR, 'button[aria-label="Increase minutes"]')
    DECREASE_MINUTE = (By.CSS_SELECTOR, 'button[aria-label="Decrease minutes"]')
    PERIOD_TOGGLE = (
        By.XPATH,
        "//div[@data-field='eventTime']//button[normalize-space(text())='AM' or normalize-space(text())='PM']",
    )

    PERFORMING_LANGUAGE_BUTTON = (By.CSS_SELECTOR, '[data-field="performingLanguage"] [role="button"]')

    LOCATION_INPUT = (By.CSS_SELECTOR, '[data-field="eventLocationSearch"] input')
    USE_CURRENT_LOCATION_BUTTON = (By.XPATH, "//button[.//text()[contains(., 'Use Current Location')]]")
    MAP_SELECT_LOCATION_BUTTON = (By.XPATH, "//button[normalize-space(text())='Select Location']")
    MAP_CANCEL_BUTTON = (By.XPATH, "//button[normalize-space(text())='Cancel']")
    AUTO_FILLED_INPUTS = (By.CSS_SELECTOR, 'input[placeholder="Auto-filled"]')
    STATE_INPUT = (By.CSS_SELECTOR, 'input[placeholder="e.g., Haryana"]')

    CHECK_SERVICEABILITY_BUTTON = (By.XPATH, "//button[.//text()[contains(., 'Check Serviceability')]]")
    SERVICE_AVAILABLE_BADGE = (By.XPATH, "//*[contains(text(), 'Service Available')]")
    SERVICE_UNAVAILABLE_BADGE = (By.XPATH, "//*[contains(text(), 'Service') and contains(text(), 'Unavailable')]")
    PREVIOUS_BUTTON = (By.XPATH, "//button[.//text()[contains(., 'Previous')]]")

    @staticmethod
    def _option(label: str):
        return (By.XPATH, f"//*[self::li or self::div or self::p][normalize-space(text())='{label}']")

    @staticmethod
    def _day_cell(day: int):
        return (
            By.XPATH,
            "//div[contains(@class,'react-datepicker__day') and "
            "not(contains(@class,'outside-month')) and "
            "not(contains(@class,'react-datepicker__day--disabled')) and "
            f"normalize-space(text())='{day}']",
        )

    def select_event_type(self, label: str, attempts: int = 4):
        # Same custom-dropdown re-render race as open_calendar/select_location_suggestion:
        # a click on the option can land mid-re-render and silently do nothing, leaving
        # the dropdown open with the placeholder unchanged (observed via real failed
        # runs - see docs/test_execution_summary.md). EVENT_TYPE_BUTTON is a toggle, so
        # a retry must only click it when the option isn't already visible - blindly
        # re-clicking it on every attempt closes an already-open dropdown and then waits
        # out the full timeout for an option that will never appear (this was an earlier,
        # broken version of this fix - see git history / test_execution_summary.md).
        option_locator = self._option(label)
        for attempt in range(1, attempts + 1):
            try:
                if not self.is_visible(option_locator, timeout=1):
                    self.click(self.EVENT_TYPE_BUTTON)
                self.click(option_locator)
                self.wait.until(lambda d: label in self.find(self.EVENT_TYPE_BUTTON).text)
                return
            except TimeoutException:
                logger.warning("Event type selection did not register on attempt %s/%s", attempt, attempts)
        raise TimeoutException(f"Selecting event type {label!r} never updated the Event Type button")

    def open_calendar(self, attempts: int = 4):
        # NOTE: react-datepicker's outside-click handler closes the calendar immediately
        # when it is opened via a JS-dispatched (execute_script) click - a real pointer
        # click is required. This early in the page the field can sit close enough to
        # the top that scrollIntoView can't clear the sticky promo bar (there isn't
        # enough content above it to scroll further), so ActionChains is used to issue
        # a genuine click at the element instead of Selenium's elementFromPoint-checked
        # WebElement.click(), which the sticky bar intercepts. Opening the popper is
        # occasionally flaky against this live staging app (observed during manual
        # exploration too), so a small, logged retry is used - see
        # docs/test_execution_summary.md.
        last_error = None
        for attempt in range(1, attempts + 1):
            # Alternate between the calendar icon and the date input itself as the
            # click target - both open the same picker, and using a different target
            # on retry avoids repeating whatever made the previous attempt fail.
            target_locator = self.EVENT_DATE_CALENDAR_BUTTON if attempt % 2 else self.EVENT_DATE_INPUT
            target = self.wait_clickable(target_locator)
            self.scroll_into_view(target)
            ActionChains(self.driver).move_to_element(target).click().perform()
            try:
                WebDriverWait(self.driver, 4).until(EC.visibility_of_element_located(self.DATEPICKER_POPPER))
                return
            except TimeoutException as exc:
                last_error = exc
                logger.warning("Calendar popper did not open on attempt %s/%s", attempt, attempts)
        raise last_error

    def select_date_day(self, day: int):
        self.click(self._day_cell(day))

    def get_event_date_value(self) -> str:
        return self.find(self.EVENT_DATE_INPUT).get_attribute("value")

    def increase_hour(self, times: int = 1):
        for _ in range(times):
            self.click(self.INCREASE_HOUR)

    def increase_minute(self, times: int = 1):
        for _ in range(times):
            self.click(self.INCREASE_MINUTE)

    def set_period(self, period: str):
        button = self.find(self.PERIOD_TOGGLE)
        if button.text.strip().upper() != period.upper():
            self.scroll_into_view(button)
            button.click()

    def select_performing_language(self, label: str):
        self.click(self.PERFORMING_LANGUAGE_BUTTON)
        self.click(self._option(label))

    def search_location(self, query: str):
        field = self.wait_visible(self.LOCATION_INPUT)
        self.scroll_into_view(field)
        self.driver.execute_script("arguments[0].focus();", field)
        field.send_keys(query)

    _SUGGESTION_LOCATOR = (By.XPATH, "//div[contains(@class,'cursor-pointer')][.//text()[contains(.,',')]]")

    def get_location_suggestion_texts(self) -> list:
        # Suggestions come from an async, network-backed autocomplete with no loading
        # indicator to hook an explicit wait on; poll for the list to stop being empty
        # rather than sleeping a fixed amount.
        try:
            self.wait.until(lambda d: len(d.find_elements(*self._SUGGESTION_LOCATOR)) > 0)
        except TimeoutException:
            return []
        candidates = self.find_all(self._SUGGESTION_LOCATOR)
        return [c.text.strip() for c in candidates if c.text.strip()]

    def select_location_suggestion(self, index_or_text=0, attempts: int = 4):
        """Selects a suggestion row from the same list get_location_suggestion_texts()
        reads (by position - default the first/top result). A real pointer click
        (ActionChains) is used because a plain WebElement.click()/JS click on this
        custom autocomplete list was observed to sometimes register no selection at
        all here, the same class of issue as the datepicker toggle (see open_calendar).
        Retries against a freshly-queried row and verifies the search field actually
        changed, since a click landing mid-re-render can silently do nothing.

        index_or_text: an int row index (default 0, the top suggestion), or a string
        naming which suggestion to pick by its text (kept for readability in tests)."""
        field = self.find(self.LOCATION_INPUT)
        value_before = field.get_attribute("value")

        for attempt in range(1, attempts + 1):
            # The suggestion list is async and can briefly flicker empty between
            # keystrokes/re-renders, so this is re-checked on every attempt rather than
            # once before the loop.
            self.wait.until(lambda d: len(d.find_elements(*self._SUGGESTION_LOCATOR)) > 0)
            candidates = self.find_all(self._SUGGESTION_LOCATOR)
            if not candidates:
                continue
            if isinstance(index_or_text, int):
                row = candidates[min(index_or_text, len(candidates) - 1)]
            else:
                row = next((c for c in candidates if index_or_text in c.text), candidates[0])
            self.scroll_into_view(row)
            ActionChains(self.driver).move_to_element(row).click().perform()
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda d: self.find(self.LOCATION_INPUT).get_attribute("value") != value_before
                )
                return
            except TimeoutException:
                logger.warning("Location suggestion click had no effect on attempt %s/%s", attempt, attempts)
        raise TimeoutException(f"Selecting location suggestion {index_or_text!r} never updated the search field")

    def confirm_map_location(self):
        self.click(self.MAP_SELECT_LOCATION_BUTTON)

    def _wait_for_auto_filled_fields(self):
        self.wait.until(lambda d: len(d.find_elements(*self.AUTO_FILLED_INPUTS)) >= 2)

    def get_pincode(self) -> str:
        self._wait_for_auto_filled_fields()
        return self.find_all(self.AUTO_FILLED_INPUTS)[0].get_attribute("value")

    def get_city(self) -> str:
        self._wait_for_auto_filled_fields()
        return self.find_all(self.AUTO_FILLED_INPUTS)[1].get_attribute("value")

    def get_state(self) -> str:
        return self.find(self.STATE_INPUT).get_attribute("value")

    def check_serviceability(self):
        self.click(self.CHECK_SERVICEABILITY_BUTTON)

    def is_service_available(self) -> bool:
        return self.is_visible(self.SERVICE_AVAILABLE_BADGE, timeout=10)

    def click_previous(self):
        self.click(self.PREVIOUS_BUTTON)
