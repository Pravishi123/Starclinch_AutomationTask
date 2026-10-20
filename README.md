# Express Booking QA Automation

Selenium + Pytest automation and manual QA deliverable for StarClinch's **Express
Booking** flow.

## Project Overview

This repository tests the real, live Express Booking booking wizard end-to-end: artist
preferences and budget-tier selection, event details (type/date/time/language),
location search and serviceability, contact information, and the Review & Pay summary
— stopping deliberately before any real payment. It includes both a Selenium/Pytest
automation framework and a full manual QA artifact set (scenarios, detailed test
cases, bug reports, execution summary), all grounded in the actual observed behavior
of the staging application rather than assumptions.

## Application

```
https://sv2.starclinch.com/express-booking/
```

The real booking wizard lives at `https://sv2.starclinch.com/express-booking/on-demand`
(reached via the "RESERVE NOW" CTA on the landing page).

Mandatory location used throughout: **Jaunpur, Uttar Pradesh, India**.

## Technology

- Python 3.x
- Selenium WebDriver (Chrome primary; Firefox supported via Selenium Manager but
  unverified in this environment — see Known Limitations)
- Pytest, with markers for smoke/e2e/negative/validation/regression
- Page Object Model (POM)
- Explicit `WebDriverWait` waits throughout — no blanket `time.sleep()`
- `pytest-html` for the execution report
- Automatic screenshot capture on test failure

## Prerequisites

- Python 3.12+
- Google Chrome installed

## Installation

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```
Linux/macOS:
```bash
source .venv/bin/activate
```

Then:
```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest -v
pytest -v -m smoke
pytest -v -m e2e
pytest -v -m validation
pytest -v -m negative
pytest -v --html=reports/report.html --self-contained-html
```

Browser/headless options (both implemented and exercised):
```bash
pytest -v --browser=chrome
pytest -v --browser=chrome --headless
pytest -v --browser=firefox   # coded, not verified in this environment (no local Firefox)
```

## Framework Architecture

```
config/          base URL, timeouts, output paths
pages/           one Page Object per real wizard step/section
  base_page.py         shared wait/click/type helpers, no business logic
  express_booking_page.py   Step 1: Artist Selection (preferences, offer, budget tier)
  event_details_page.py     Step 2: event type/date/time/language/location + serviceability
  contact_page.py           Contact Information (renders on Step 2, after serviceability)
  review_page.py            Step 3: Booking Summary + Venue & Contact card
  payment_page.py           Payment-option reading only - never submits payment
tests/           test_express_booking.py (E2E), test_validations.py, test_negative_scenarios.py
test_data/       synthetic test data, no real personal or payment data
utils/           driver_factory, logger, screenshot capture
docs/            manual QA artifacts (see below)
reports/         generated pytest-html report + execution log
screenshots/     failure screenshots + curated bug-evidence screenshots
```

Tests read as business flows built from page-object methods
(`booking_page.select_budget_tier(...)`, `event_page.check_serviceability()`,
`review_page.get_venue_and_contact_text()`), not raw `driver.find_element(...)` calls.

## Test Data Approach

All test data lives in `test_data/test_data.py`, separate from test logic — synthetic
names/emails/phones, the mandatory Jaunpur location string, and negative/boundary value
sets. No secrets, passwords, OTPs, or real personal data are used or required, since no
step in this flow needs a login and automation never reaches real payment.

## Synchronization Strategy

Every page object waits explicitly (`WebDriverWait` via `base_page.py`) rather than
sleeping. Two documented exceptions exist for genuinely flaky real-app interactions,
both logged rather than hidden:
- The Event Date calendar popover and the location-suggestion list occasionally do not
  register a click dispatched as a JS/synthetic event or land mid-re-render; a native/
  `ActionChains` click plus a short, logged verify-and-retry loop is used instead of a
  blind sleep (see `pages/event_details_page.py`).
- A handful of CTAs can be intercepted by the sticky top promo bar or another
  absolutely-positioned overlay depending on scroll position, even after
  `scrollIntoView`; `base_page.click()` attempts a native click first and falls back to
  a logged JS click only on `ElementClickInterceptedException`.

## Reporting

```bash
pytest -v --html=reports/report.html --self-contained-html
```
Produces a single self-contained HTML file with pass/fail/skip status per test.

## Screenshots

`conftest.py` implements `pytest_runtest_makereport` to capture a screenshot to
`screenshots/` whenever a test fails, named `<test_name>_<timestamp>.png`, without
masking the original assertion/exception. `screenshots/evidence/` holds a curated set
of screenshots referenced from `docs/bug_reports.md`.

## Known Staging Limitations

- **Payment is never triggered.** Automation stops at the Review & Pay screen once the
  "Securely Pay ₹99" button is confirmed present — it is never clicked. See
  `docs/test_execution_summary.md` for the exact stopping point.
- **Firefox is coded but unverified** in this environment (no local Firefox install at
  build time). `utils/driver_factory.py` supports it via Selenium Manager the same way
  as Chrome.
- **Some real-app interactions are intermittently flaky** against this live staging
  instance (calendar popover, location-suggestion click) — mitigated with logged,
  bounded retries rather than papered over silently. See `docs/bug_reports.md`
  "Observations" for the underlying cause.
- **Contact Information only exists in the DOM after "Check Serviceability" succeeds**
  — tests that need contact fields must complete event details + location +
  serviceability first (see `_reach_contact_section` in `tests/test_validations.py`).

## Manual QA Artifacts

- [Manual Test Scenarios](docs/manual_test_scenarios.md)
- [Detailed Test Cases](docs/detailed_test_cases.md)
- [Bug Reports](docs/bug_reports.md)
- [Test Execution Summary](docs/test_execution_summary.md)

## Safety

No test in this repository ever completes a real financial transaction. The E2E test
explicitly stops the instant the final "Securely Pay ₹99" button is confirmed visible.
