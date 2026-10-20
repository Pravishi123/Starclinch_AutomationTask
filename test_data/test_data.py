"""Synthetic test data. No real names, phone numbers, emails, or payment details."""

MANDATORY_LOCATION_QUERY = "Jaunpur"
MANDATORY_LOCATION_FULL = "Jaunpur, Uttar Pradesh, India"

VALID_CONTACT = {
    "name": "Ananya QA Test",
    "email": "ananya.qatest@example.com",
    "phone": "9876543210",
}

VALID_EVENT = {
    "event_type": "Birthday Party",
    "date_day_offset": 4,  # days from today, kept comfortably inside the current month
    "hour_increments": 1,
    "minute_increments": 1,  # each click moves the minute stepper by 15
    "period": "PM",
    "language": "Hindi",
}

BUDGET_TIER = "Value"

INVALID_EMAILS = [
    "plainaddress",
    "test@",
    "@test.com",
    "test.com",
    "test@domain",
]

# Observed real behavior: the app trims surrounding whitespace before validating, so
# these are accepted (a reasonable design choice, not a defect) - see
# docs/manual_test_scenarios.md and docs/bug_reports.md "Observations".
EMAILS_WITH_WHITESPACE_ACCEPTED = [
    " test@domain.com",
    "test@domain.com ",
]

INVALID_PHONES = {
    "too_short": "123",
    "too_long": "123456789012345",
    "alphabetic": "abcdefghij",
    "special_chars": "98765-4321!",
    "blank": "",
}

INVALID_LOCATIONS = [
    "asdkjhaskjdhaskjdh",  # nonsense string, expected to yield no suggestions
    "Zzyzznotarealplace",
]

PARTIAL_LOCATION_QUERY = "Jaun"

UNICODE_NAME = "Ānanya QA Tëst 测试"
LONG_NAME = "A" * 300
WHITESPACE_ONLY = "   "
