"""Positive end-to-end journey through the real Express Booking flow, stopping at the
last safely-testable screen. No step in this test ever clicks the 'Securely Pay'
button - see docs/test_execution_summary.md for exactly where automation stops and why.
"""
import datetime

import pytest

from pages.express_booking_page import ExpressBookingPage
from pages.event_details_page import EventDetailsPage
from pages.contact_page import ContactPage
from pages.review_page import ReviewPage
from pages.payment_page import PaymentPage
from test_data.test_data import VALID_CONTACT, VALID_EVENT, BUDGET_TIER, MANDATORY_LOCATION_QUERY


@pytest.mark.smoke
@pytest.mark.e2e
def test_complete_booking_journey_reaches_payment_step(driver):
    booking_page = ExpressBookingPage(driver)
    booking_page.open()
    assert "Express" in driver.title, f"Unexpected page title: {driver.title}"

    # --- Step 1: Artist Selection ---
    booking_page.select_artist_type()
    booking_page.select_artist_preference()
    booking_page.select_event_duration("45 mins")
    booking_page.select_offer_type(new_users_only=True)

    tier_prices = booking_page.get_budget_tier_prices(BUDGET_TIER)
    booking_page.click_next()
    # Note: the app shows "Please pick an option" on this sub-step by default, before
    # any Next click is attempted with a tier unselected - see docs/bug_reports.md.
    booking_page.select_budget_tier(BUDGET_TIER)
    booking_page.click_next()

    # --- Step 2: Event Details ---
    event_page = EventDetailsPage(driver)
    event_page.select_event_type(VALID_EVENT["event_type"])

    target_date = datetime.date.today() + datetime.timedelta(days=VALID_EVENT["date_day_offset"])
    event_page.open_calendar()
    event_page.select_date_day(target_date.day)
    displayed_date = event_page.get_event_date_value()
    assert str(target_date.year) in displayed_date, (
        f"Event date input shows {displayed_date!r}, expected year {target_date.year}"
    )

    event_page.increase_hour(VALID_EVENT["hour_increments"])
    event_page.increase_minute(VALID_EVENT["minute_increments"])
    event_page.set_period(VALID_EVENT["period"])

    event_page.search_location(MANDATORY_LOCATION_QUERY)
    suggestions = event_page.get_location_suggestion_texts()
    assert any(MANDATORY_LOCATION_QUERY in s for s in suggestions), (
        f"No suggestion for {MANDATORY_LOCATION_QUERY!r} in {suggestions}"
    )
    event_page.select_location_suggestion(0)
    event_page.confirm_map_location()

    pincode = event_page.get_pincode()
    state = event_page.get_state()
    assert pincode, "Pincode was not auto-filled after confirming the map location"
    assert state == "Uttar Pradesh", f"Expected state 'Uttar Pradesh', got {state!r}"

    event_page.check_serviceability()
    assert event_page.is_service_available(), f"Expected {MANDATORY_LOCATION_QUERY} to be serviceable"

    contact_page = ContactPage(driver)
    contact_page.enter_contact_details(**VALID_CONTACT)
    contact_page.proceed_to_checkout()

    # --- Step 3: Review & Pay ---
    review_page = ReviewPage(driver)
    assert VALID_EVENT["event_type"] in review_page.get_event_type()

    date_and_time = review_page.get_date_and_time()
    assert target_date.strftime("%d/%m/%Y") in date_and_time, (
        f"Review date/time {date_and_time!r} does not contain expected date {target_date:%d/%m/%Y}"
    )

    if tier_prices.get("discounted_price"):
        offers_text = review_page.get_offers_applied()
        assert offers_text, "Expected an 'Offers Applied' value on the review screen"

    review_page.expand_venue_and_contact()
    venue_and_contact_text = review_page.get_venue_and_contact_text()
    assert VALID_CONTACT["name"] in venue_and_contact_text
    assert VALID_CONTACT["email"] in venue_and_contact_text
    # The review screen formats the number as "+91 98765 43210" - compare digits only.
    displayed_digits = "".join(ch for ch in venue_and_contact_text if ch.isdigit())
    assert VALID_CONTACT["phone"] in displayed_digits

    payment_page = PaymentPage(driver)
    assert payment_page.is_pay_now_visible()
    assert payment_page.is_pay_upon_arrival_visible()
    assert payment_page.is_securely_pay_button_present(), (
        "Did not reach the final pre-payment screen"
    )
    # Safety rule: the test stops here. 'Securely Pay' is never clicked.
