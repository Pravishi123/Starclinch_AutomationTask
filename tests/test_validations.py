"""Field-level validation and boundary scenarios for the Event Details / Contact step.

Assertions here check *observed* application behavior (does the form block
progression, does an inline error appear) rather than presuming exact wording that
was never seen during exploration - see docs/manual_test_scenarios.md for the full
manual matrix these automate a subset of.
"""
import datetime

import pytest

from pages.review_page import ReviewPage
from test_data.test_data import (
    VALID_CONTACT,
    VALID_EVENT,
    INVALID_EMAILS,
    INVALID_PHONES,
    MANDATORY_LOCATION_QUERY,
    PARTIAL_LOCATION_QUERY,
    UNICODE_NAME,
    LONG_NAME,
    WHITESPACE_ONLY,
    EMAILS_WITH_WHITESPACE_ACCEPTED,
)


def _complete_minimum_event_fields(event_details_page):
    event_details_page.select_event_type(VALID_EVENT["event_type"])
    event_details_page.open_calendar()
    target_day = (datetime.date.today() + datetime.timedelta(days=3)).day
    event_details_page.select_date_day(target_day)
    event_details_page.increase_hour(1)
    event_details_page.increase_minute(1)


def _reach_contact_section(event_details_page):
    """Contact Information only renders after Check Serviceability succeeds - it is
    not present on the page before that, so every test touching contact_page must
    complete event details + location + serviceability first."""
    _complete_minimum_event_fields(event_details_page)
    event_details_page.search_location(MANDATORY_LOCATION_QUERY)
    event_details_page.select_location_suggestion(0)
    event_details_page.confirm_map_location()
    event_details_page.check_serviceability()
    assert event_details_page.is_service_available(), "Setup requires Jaunpur to be serviceable"


@pytest.mark.validation
def test_proceed_blocked_when_contact_fields_are_blank(event_details_page, contact_page):
    _reach_contact_section(event_details_page)
    contact_page.proceed_to_checkout()

    review_page = ReviewPage(event_details_page.driver)
    assert not review_page.is_visible(review_page.VENUE_CONTACT_TOGGLE, timeout=3), (
        "Booking advanced to Review & Pay despite blank required contact fields"
    )


@pytest.mark.validation
@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
def test_malformed_email_does_not_proceed(event_details_page, contact_page, invalid_email):
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(VALID_CONTACT["name"])
    contact_page.enter_email(invalid_email)
    contact_page.enter_phone(VALID_CONTACT["phone"])
    contact_page.proceed_to_checkout()

    review_page = ReviewPage(event_details_page.driver)
    assert not review_page.is_visible(review_page.VENUE_CONTACT_TOGGLE, timeout=3), (
        f"Booking advanced to Review & Pay with malformed email {invalid_email!r}"
    )


@pytest.mark.validation
@pytest.mark.parametrize("case_name,invalid_phone", list(INVALID_PHONES.items()))
def test_malformed_phone_does_not_proceed(event_details_page, contact_page, case_name, invalid_phone):
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(VALID_CONTACT["name"])
    contact_page.enter_email(VALID_CONTACT["email"])
    contact_page.enter_phone(invalid_phone)
    contact_page.proceed_to_checkout()

    review_page = ReviewPage(event_details_page.driver)
    assert not review_page.is_visible(review_page.VENUE_CONTACT_TOGGLE, timeout=3), (
        f"Booking advanced to Review & Pay with invalid phone case {case_name!r} ({invalid_phone!r})"
    )


@pytest.mark.validation
@pytest.mark.parametrize("email_with_whitespace", EMAILS_WITH_WHITESPACE_ACCEPTED)
def test_email_with_surrounding_whitespace_is_trimmed_and_accepted(event_details_page, contact_page, email_with_whitespace):
    """Observed real behavior: the app trims leading/trailing whitespace before
    validating an otherwise-valid email, so booking proceeds normally. This is a
    reasonable design choice, not a defect - see docs/bug_reports.md."""
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(VALID_CONTACT["name"])
    contact_page.enter_email(email_with_whitespace)
    contact_page.enter_phone(VALID_CONTACT["phone"])
    contact_page.proceed_to_checkout()

    review_page = ReviewPage(event_details_page.driver)
    assert review_page.is_visible(review_page.VENUE_CONTACT_TOGGLE, timeout=5), (
        f"Expected email {email_with_whitespace!r} to be trimmed and accepted"
    )


@pytest.mark.validation
def test_partial_location_query_still_offers_jaunpur(event_details_page):
    event_details_page.search_location(PARTIAL_LOCATION_QUERY)
    suggestions = event_details_page.get_location_suggestion_texts()
    assert any(MANDATORY_LOCATION_QUERY in s for s in suggestions), (
        f"Partial query {PARTIAL_LOCATION_QUERY!r} did not surface a Jaunpur suggestion: {suggestions}"
    )


@pytest.mark.validation
def test_contact_name_accepts_unicode(event_details_page, contact_page):
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(UNICODE_NAME)
    value = contact_page.find(contact_page.FULL_NAME_INPUT).get_attribute("value")
    assert value == UNICODE_NAME, f"Unicode name was altered/truncated: {value!r}"


@pytest.mark.validation
def test_contact_name_field_handles_unusually_long_input(event_details_page, contact_page):
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(LONG_NAME)
    value = contact_page.find(contact_page.FULL_NAME_INPUT).get_attribute("value")
    assert len(value) <= len(LONG_NAME), "Field accepted more characters than were typed"


@pytest.mark.validation
def test_whitespace_only_name_does_not_proceed(event_details_page, contact_page):
    _reach_contact_section(event_details_page)
    contact_page.enter_full_name(WHITESPACE_ONLY)
    contact_page.enter_email(VALID_CONTACT["email"])
    contact_page.enter_phone(VALID_CONTACT["phone"])
    contact_page.proceed_to_checkout()

    review_page = ReviewPage(event_details_page.driver)
    assert not review_page.is_visible(review_page.VENUE_CONTACT_TOGGLE, timeout=3), (
        "Booking advanced to Review & Pay with a whitespace-only name"
    )
