import datetime

import pytest

from config.config import DEFAULT_BROWSER, HEADLESS
from pages.express_booking_page import ExpressBookingPage
from pages.event_details_page import EventDetailsPage
from pages.contact_page import ContactPage
from test_data.test_data import BUDGET_TIER
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import capture

logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=DEFAULT_BROWSER, help="chrome or firefox")
    parser.addoption("--headless", action="store_true", default=HEADLESS, help="run browser headlessly")


@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    drv = create_driver(browser=browser, headless=headless)
    yield drv
    logger.info("Quitting driver")
    drv.quit()


@pytest.fixture(scope="function")
def event_details_page(driver):
    """Drives Step 1 (Artist Selection) with default valid data and lands on Step 2
    (Event Details), for tests that only care about fields on that step."""
    booking_page = ExpressBookingPage(driver)
    booking_page.open()
    booking_page.select_artist_type()
    booking_page.select_artist_preference()
    booking_page.select_event_duration()
    booking_page.select_offer_type(new_users_only=True)
    booking_page.click_next()
    booking_page.select_budget_tier(BUDGET_TIER)
    booking_page.click_next()
    return EventDetailsPage(driver)


@pytest.fixture(scope="function")
def contact_page(driver):
    return ContactPage(driver)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                path = capture(driver, item.name, timestamp)
                logger.error("Test %s failed - screenshot saved to %s", item.name, path)
            except Exception as exc:  # pragma: no cover - screenshot capture must never mask the real failure
                logger.error("Screenshot capture failed for %s: %s", item.name, exc)
