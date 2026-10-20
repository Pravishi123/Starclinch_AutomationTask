"""Negative-path scenarios: invalid location input, unselected autocomplete text,
disabled past dates, and a controlled double-click check on the Next CTA."""
import datetime

import pytest
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from pages.express_booking_page import ExpressBookingPage
from test_data.test_data import INVALID_LOCATIONS, BUDGET_TIER


@pytest.mark.negative
def test_invalid_location_yields_no_suggestions(event_details_page):
    for bogus_location in INVALID_LOCATIONS:
        event_details_page.search_location(bogus_location)
        suggestions = event_details_page.get_location_suggestion_texts()
        assert suggestions == [], (
            f"Expected no suggestions for nonsense location {bogus_location!r}, got {suggestions}"
        )
        event_details_page.type_text(event_details_page.LOCATION_INPUT, "")


@pytest.mark.negative
def test_typed_but_unselected_location_leaves_fields_unfilled(event_details_page):
    event_details_page.search_location("Jaunpur")
    # Deliberately do not click a suggestion.
    pincode_inputs = event_details_page.find_all(event_details_page.AUTO_FILLED_INPUTS)
    for field in pincode_inputs:
        assert field.get_attribute("value") == "", (
            "Pincode/City auto-filled even though no autocomplete suggestion was selected"
        )


@pytest.mark.negative
def test_past_dates_are_disabled_in_calendar(event_details_page):
    event_details_page.open_calendar()
    today = datetime.date.today()
    if today.day > 1:
        past_day_cell = event_details_page.find(
            (
                By.XPATH,
                f"//div[contains(@class,'react-datepicker__day') and normalize-space(text())='{today.day - 1}']",
            )
        )
        classes = past_day_cell.get_attribute("class")
        assert "disabled" in classes, f"Expected past date to be disabled, class was {classes!r}"


@pytest.mark.negative
def test_double_click_next_does_not_skip_a_step(driver):
    booking_page = ExpressBookingPage(driver)
    booking_page.open()
    booking_page.select_artist_type()
    booking_page.select_artist_preference()
    booking_page.select_event_duration()
    booking_page.select_offer_type(new_users_only=True)

    booking_page.click(booking_page.NEXT_BUTTON)
    next_button = booking_page.wait_clickable(booking_page.NEXT_BUTTON)
    try:
        next_button.click()  # deliberate, controlled double-click - not a load test
    except (StaleElementReferenceException, ElementClickInterceptedException):
        pass  # the step already re-rendered/shifted between the two clicks - no duplicate action possible

    event_type_field = (By.CSS_SELECTOR, '[data-field="eventType"]')
    assert not booking_page.is_visible(event_type_field, timeout=3), (
        "Double-clicking Next with no budget tier selected skipped straight to the "
        "Event Details step (step 2), instead of staying on Artist Selection"
    )
