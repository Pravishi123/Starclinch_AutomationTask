# Bug Reports — Express Booking

Both defects below were reproduced twice: once during manual exploratory testing (real
Chrome, DOM inspection) and again independently via the automated Selenium suite
(`tests/test_express_booking.py`), which strengthens confidence these are genuine,
consistent product behaviors rather than one-off flukes.

---

## BUG-EB-001 — Location autocomplete suggestion labels duplicate the state/country segment

- **Environment:** Staging, `https://sv2.starclinch.com/express-booking/on-demand`
- **Browser:** Chrome 151 (Windows 11)
- **Preconditions:** On the Event Details step, Event Location field focused
- **Steps to Reproduce:**
  1. Navigate to the Event Details step (step 2)
  2. Type `Jaunpur` into the "Event Location" field
  3. Read the primary text of any returned suggestion
- **Expected Result:** A suggestion label should read the place name once, e.g.
  `Jaunpur, Uttar Pradesh, India`
- **Actual Result:** Every suggestion repeats its trailing state/country segment, e.g.:
  - `Jaunpur, Uttar Pradesh, India, Uttar Pradesh, India`
  - `Jaunpur Bus Stand, Husainabad, Jaunpur, Uttar Pradesh, India, Husainabad, Jaunpur, Uttar Pradesh, India`
  - `Jaunpur Junction railway station, Khasanpur, Jaunpur, Etakadpur, Uttar Pradesh, India, Khasanpur, Jaunpur, Etakadpur, Uttar Pradesh, India`

  This affects **all** suggestions returned for the query, not an isolated row —
  consistent with the label being built by concatenating a full formatted address with
  its own secondary/subtitle line instead of showing them once.
- **Severity:** Low (cosmetic/readability — does not block booking, the correct place
  is still selectable and resolves to the right map pin)
- **Priority:** Medium (visible on every single location search, so it is high-frequency
  even though low-impact)
- **Reproducibility:** 100% (every suggestion, every search attempted)
- **Evidence:** `screenshots/evidence/BUG-EB-001_autocomplete_duplicate_text.png`

---

## BUG-EB-002 — Selecting "Jaunpur" auto-fills City as "Prayagraj" instead of "Jaunpur"

- **Environment:** Staging, `https://sv2.starclinch.com/express-booking/on-demand`
- **Browser:** Chrome 151 (Windows 11)
- **Preconditions:** On the Event Details step, a location suggestion for the mandatory
  test location has just been selected
- **Steps to Reproduce:**
  1. Type `Jaunpur` into "Event Location" and select the top suggestion
     (`Jaunpur, Uttar Pradesh, India, Uttar Pradesh, India` — see BUG-EB-001)
  2. In the "Select Location" map modal, confirm the pin without moving it (the pin is
     already correctly centered on Jaunpur city)
  3. Click "Select Location" to confirm
  4. Read the auto-filled Pin Code / City / State fields
  5. Click "Check Serviceability"
  6. Proceed through Contact Information to Review & Pay and expand
     "Venue & Contact Details"
- **Expected Result:** City should read "Jaunpur" (matching the searched/selected
  place and the correctly-centered map pin)
- **Actual Result:**
  - Pin Code auto-fills as `222001` — a genuine Jaunpur postal code (**correct**)
  - State auto-fills as `Uttar Pradesh` (**correct**)
  - City auto-fills as **`Prayagraj`** (**incorrect** — Prayagraj is a different city,
    roughly 60 km from Jaunpur)
  - The resolved Event Location value becomes:
    `12a, Rambagh, Prayagraj, Jaunpur, Uttar Pradesh 222001, India`
  - This incorrect City value is **not corrected at any later step** — it is carried
    through unchanged to the Review & Pay screen's Venue summary, which displays:
    `12a, Rambagh, Prayagraj, Jaunpur, Uttar Pradesh 222001, India · Prayagraj, Uttar Pradesh · Pin 222001`
  - Despite the City mismatch, "Check Serviceability" still returns "Service
    Available" — serviceability appears to be computed from map coordinates/pincode,
    not from the (wrong) City text, so the booking is not blocked, but the
    customer-facing address record the user reviews and would confirm is factually
    wrong.
- **Severity:** High (a customer booking for Jaunpur would see and confirm "Prayagraj"
  as their event city on the final review/payment screen — a real risk of artist
  dispatch confusion, customer distrust, or a support escalation, even though the
  underlying pincode/coordinates are correct)
- **Priority:** High
- **Reproducibility:** 100% (reproduced identically via manual exploration and via the
  independent automated E2E test, across separate runs)
- **Evidence:**
  - `screenshots/evidence/BUG-EB-002_city_shows_prayagraj.png` (Event Details step,
    fields freshly auto-filled)
  - `screenshots/evidence/evidence_review_venue_contact.png` (same defect, carried
    through to Review & Pay)

---

## Observations (not filed as defects — insufficient evidence or by-design)

- **"Please pick an option" shown pre-emptively.** On the Artist Selection step, after
  clicking Next once (before ever attempting to submit with the budget tier
  unselected), the "Please pick an option" validation text is already visible under
  the tier tiles. This could be considered premature/always-on validation rather than
  submit-triggered validation. Not filed as a defect because it is arguably a
  legitimate "this field is required" hint pattern rather than an error state, and it
  does not block correct usage.
- **"Your Booking Expert" shows placeholder dashes.** On Review & Pay, the assigned
  expert's name renders as "—" / "—" with a broken avatar image, even after the page
  has fully settled. This may be intentional (an expert may only be assigned after
  payment/confirmation) — not enough evidence was gathered to call this a defect
  without knowing the intended behavior.
- **Automation-environment note (not a product bug):** the Event Date calendar popover
  and the location-suggestion list occasionally do not register a click dispatched via
  `execute_script`-based JS clicks or land mid-re-render; a native/ActionChains click
  with a short verify-and-retry loop was needed for reliable automation. Documented in
  `pages/event_details_page.py` and `docs/test_execution_summary.md` since this affects
  automation stability, not end-user behavior (a real mouse click did not exhibit this).

- **Leading/trailing whitespace in email is trimmed and accepted.** Entering
  `" test@domain.com"` or `"test@domain.com "` proceeds to Review & Pay normally.
  This is reasonable, expected trimming behavior (most systems do this), not a
  defect — confirmed via automated test
  `test_email_with_surrounding_whitespace_is_trimmed_and_accepted`.

No other genuine, reproducible product defects were identified during this
engagement's exploration and test execution.
