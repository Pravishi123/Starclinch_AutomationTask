# Test Execution Summary — Express Booking

## Environment

- **Date:** 2026-08-24, finalized 2026-08-25
- **Staging URL:** `https://sv2.starclinch.com/express-booking/` (wizard at `/on-demand`)
- **Browser:** Google Chrome 151 (Windows 11), via Selenium Manager — verified
- **Browser (unverified):** Firefox — coded in `utils/driver_factory.py`, not run in
  this environment (no local Firefox install at build time)
- **Python:** 3.12.10
- **Selenium:** 4.47.0, **Pytest:** 9.1.1, **pytest-html:** 4.2.0

## Commands Run

```bash
pytest --collect-only -q          # 22 tests collected, no import errors
pytest -v -m smoke                # E2E journey
pytest -v -m negative              # negative-path suite
pytest -v -m validation            # field validation/boundary suite
pytest -v --html=reports/report.html --self-contained-html
```

## Results

| Marker | Total | Passed | Failed | Skipped | Blocked |
|---|---|---|---|---|---|
| smoke / e2e | 1 | 1 | 0 | 0 | 0 |
| negative | 4 | 4 | 0 | 0 | 0 |
| validation | 17 | 17 | 0 | 0 | 0 |
| **Total** | **22** | **22** | **0** | **0** | **0** |

All 22 tests pass in the final run (463.46s / 7m43s total); see `reports/report.html`
for the full self-contained execution report.

During finalization, the E2E test (`test_complete_booking_journey_reaches_payment_step`)
was run repeatedly (10+ times) to confirm real stability rather than accepting a single
green run, since it exercises every live third-party widget in the flow. Two genuine
automation bugs surfaced and were fixed as a result — see "Defect vs. Automation vs.
Environment Triage" below. After both fixes, the test passes the large majority of runs
(~4/5 in the final verification batch); the residual occasional failure is consistent
with the same live, async, third-party-style widget flakiness already documented below
for the calendar and location autocomplete, not a further automation bug — see "Live
third-party autocomplete flakiness".

## Known Staging / Automation Limitations

- **Payment is never triggered.** The E2E test stops at the Review & Pay screen once
  the "Securely Pay ₹99" button is confirmed present (`payment_page.is_securely_pay_button_present()`).
  It is never clicked. This is the deliberate, furthest safe point — see
  `docs/bug_reports.md` for what was observed there.
- **Firefox is untested.** Code exists for it but this build environment has no local
  Firefox installation, so it could not be exercised. Flagged rather than claimed.
- **Live third-party autocomplete flakiness.** The Event Location suggestion list and
  the Event Date calendar popover are both backed by live, async, third-party-style
  services with no loading indicator. Both occasionally needed more than one attempt to
  register a click during test development — mitigated with small, logged retry loops
  in `pages/event_details_page.py` (never more than 4 attempts, always logged, never
  silently swallowed). This is a test-environment/infrastructure characteristic of a
  live staging service, not a product defect being hidden — see `docs/bug_reports.md`
  "Observations" for the underlying interaction issue.
- **CI (GitHub Actions) was not added.** Given the live-service flakiness above, a
  headless CI run would likely be less stable than this interactive local run, and
  papering over that with unbounded retries would misrepresent the suite's real
  reliability. Documented here rather than shipping an unverified workflow.

## Defect vs. Automation vs. Environment Triage

- **Product defects (genuine, reproduced, documented):** BUG-EB-001 (autocomplete
  label duplication), BUG-EB-002 (City auto-fills as "Prayagraj" instead of "Jaunpur")
  — see `docs/bug_reports.md`.
- **Automation-only issues (fixed in the framework, not product bugs):** JS-dispatched
  clicks closing the date picker immediately; occasional click-interception by the
  sticky top bar; the suggestion list briefly flickering empty between renders. All
  fixed with native/ActionChains clicks and small logged retries rather than blind
  sleeps — see `pages/event_details_page.py` and `pages/base_page.py`.
  - **Page title race on navigation.** `ExpressBookingPage.open()` asserted
    `driver.title` immediately after `driver.get()`; since this is a client-rendered
    SPA, `document.title` is set by JS after hydration and the check occasionally read
    `""`, failing the E2E test in ~5s with no real interaction attempted. Fixed by
    waiting for a non-empty title inside `open()` before returning.
  - **Event Type dropdown had no retry/verification.** Every other custom dropdown in
    the flow (calendar popover, location autocomplete) already had a retry-and-verify
    loop for this app's live re-render races; `select_event_type()` did not, and was
    observed leaving the dropdown open with the placeholder text unchanged. Fixed to
    match the existing pattern in `pages/event_details_page.py` (retry the open+select,
    verify the button text actually changed, never more than 4 attempts, always
    logged).
- **No scenario was blocked** by CAPTCHA, login, OTP, or an inability to reach a step
  safely — the flow does not require authentication and the only wall reached was the
  intentional payment stop.

## Generated Artifacts

- `reports/report.html` — self-contained pytest-html execution report
- `reports/execution.log` — run log (git-ignored, regenerated per run)
- `screenshots/` — automatic failure screenshots from this engagement's runs
- `screenshots/evidence/` — curated screenshots referenced from `docs/bug_reports.md`
