# Manual Test Scenarios — Express Booking

Application under test: `https://sv2.starclinch.com/express-booking/` → real booking
wizard lives at `https://sv2.starclinch.com/express-booking/on-demand`.

All scenarios below reflect the **actual observed** flow, not an assumed one. The real
wizard has 3 steps: **1. Artist Selection** (artist preferences, offer type, budget
tier), **2. Event Details** (event type/date/time/language/location, then Contact
Information once location is serviceable), **3. Review & Pay**.

Mandatory location for all applicable scenarios: **Jaunpur, Uttar Pradesh, India**.

Safety: no scenario submits real payment. The furthest safe point is the Review & Pay
screen with the "Securely Pay ₹99" button visible but not clicked.

---

## 1. Page / UI

| # | Scenario |
|---|---|
| UI-1 | Landing page (`/express-booking/`) loads, title is "Express Artist Booking \| Instant Same-Day Confirmation – StarClinch" |
| UI-2 | "RESERVE NOW @ ₹99 only" CTA is visible and navigates to `/express-booking/on-demand` |
| UI-3 | `/on-demand` loads directly (deep link) and renders step 1 without requiring the landing page first |
| UI-4 | 3-step progress indicator (Artist Selection / Event Details / Review & Pay) is visible and reflects current step |
| UI-5 | Required fields are marked with a red `*` |
| UI-6 | Sticky top promo bar ("Trusted by 10,000+ customers...") remains visible while scrolling |

## 2. Package / Pricing Details (Artist Selection step)

The "package" concept in this app is the **budget tier** shown after choosing duration:

| # | Scenario |
|---|---|
| PKG-1 | Three budget tiers are shown: Value (1+ yrs Exp), Popular (3+ yrs Exp), Premium (5+ yrs Exp) |
| PKG-2 | Each tier shows an original price (strikethrough) and a discounted price: Value ₹8,000→₹4,000 (-50%), Popular ₹10,000→₹6,000 (-40%), Premium ₹20,000→₹16,000 (-20%) |
| PKG-3 | Selecting a tier visually highlights it |
| PKG-4 | The selected tier's discounted price is carried through unchanged to the Review & Pay "Booking Summary" (Offers Applied: "Saved ₹X") and to the "Pay Now" gross/total amount |
| PKG-5 | "Choose your booking experience" offers a "For New Users Only" (up to 50% discount, no options offered) vs "Get up to 3 options to choose from" (no discount) radio choice — default is "For New Users Only" |
| PKG-6 | The "Please pick an option" validation text under the budget tiers is shown **by default**, before the user has attempted to click Next — see `bug_reports.md` |

## 3. Event Details

| # | Scenario |
|---|---|
| EVT-1 | Artist Type dropdown offers only "Singer (with Guitar/Instrument/Karaoke)", with a "More categories coming soon" note — effectively a single-option required field |
| EVT-2 | Artist Preference (gender) dropdown offers Male Artist / Female Artist / No Preference |
| EVT-3 | Event Duration offers 45 mins / 90 mins as circular tile selectors |
| EVT-4 | Event Type (step 2) dropdown offers: Birthday Party, Private Party, House Party, Corporate, Wedding, Restaurant, Religious, Inauguration, Charity, Kid's Party, Exhibition |
| EVT-5 | Performing Language defaults to "Hindi" as a removable chip; a dropdown allows adding more languages |
| EVT-6 | Contact Information (Full Name, Email, Phone) section only renders **after** "Check Serviceability" succeeds — it does not exist in the DOM before that |

## 4. Location (mandatory: Jaunpur, Uttar Pradesh, India)

| # | Scenario |
|---|---|
| LOC-1 | Typing "Jaunpur" returns multiple autocomplete suggestions (Jaunpur city, Jaunpur Bus Stand, Jaunpur Junction, Jaunpur City Railway Station, Jaunpur District) |
| LOC-2 | Every suggestion's primary label duplicates its state/country segment, e.g. "Jaunpur, Uttar Pradesh, India, Uttar Pradesh, India" — see `bug_reports.md` BUG-EB-001 |
| LOC-3 | Selecting a suggestion opens a "Select Location" Google Map modal, pre-centered correctly on the chosen place, with a draggable pin |
| LOC-4 | Confirming the map ("Select Location") auto-fills Pin Code, City, and State |
| LOC-5 | For the Jaunpur suggestion, City auto-fills as **"Prayagraj"** instead of "Jaunpur", while Pincode (222001, a genuine Jaunpur pincode) and State ("Uttar Pradesh") are correct — see `bug_reports.md` BUG-EB-002 |
| LOC-6 | "Check Serviceability" returns "Service Available" for the Jaunpur pin despite the City-field mismatch above |
| LOC-7 | Partial query "Jaun" still surfaces Jaunpur suggestions |
| LOC-8 | Typing a nonsense string (e.g. "asdkjhaskjdhaskjdh") yields no suggestions |
| LOC-9 | Typing a location but not selecting any suggestion leaves Pin Code/City/State unfilled and does not mark the location as serviceable |
| LOC-10 | Clearing the location field (✕ icon) empties the search input |
| LOC-11 | "Use Current Location" button is present as an alternative to typing |

## 5. Date

| # | Scenario |
|---|---|
| DATE-1 | Calendar opens showing the current month with today highlighted |
| DATE-2 | Dates before today are visually disabled and carry a `react-datepicker__day--disabled` class |
| DATE-3 | A valid future date can be selected and reflects in the "Event Date" input as e.g. "Aug 28, 2026" |
| DATE-4 | The date field is not manually typable — it is a picker-only input (`readOnly`-style interaction observed) |
| DATE-5 | Selected date persists into the Review & Pay "Date & Time" summary line in `DD/MM/YYYY at hh:mm AM/PM` format |

## 6. Time

| # | Scenario |
|---|---|
| TIME-1 | Start Time uses separate hour/minute steppers (Increase/Decrease buttons) plus an AM/PM toggle, not free text entry |
| TIME-2 | Minutes step in 15-minute increments (00 → 15 → 30 → 45) |
| TIME-3 | Hour and minute both start blank ("—") until the stepper is used at least once |
| TIME-4 | Selected time persists into the Review & Pay "Date & Time" line |

## 7. Contact Details

| # | Scenario |
|---|---|
| CON-1 | Full Name, Email Address, Phone Number are required (red `*`) |
| CON-2 | Phone field shows a fixed "+91" India prefix with flag icon and placeholder "Enter number for auto-updates" |
| CON-3 | Valid contact details persist unchanged into the Review & Pay "Venue & Contact Details" card (email exact match; phone shown reformatted as "+91 98765 43210") |
| CON-4 | Blank required contact fields block "Proceed to Checkout" from reaching Review & Pay |
| CON-5 | Malformed emails (see boundary list below) block progression |
| CON-6 | Malformed phone numbers (too short/long, alphabetic, special characters, blank) block progression |
| CON-7 | Full Name accepts Unicode characters without truncation |
| CON-8 | Full Name accepts unusually long input without the framework/browser silently truncating it client-side beyond what was typed |
| CON-9 | A whitespace-only name blocks progression |

## 8. Input Robustness

| # | Scenario |
|---|---|
| ROB-1 | Empty required fields are rejected at "Proceed to Checkout" |
| ROB-2 | Whitespace-only name is rejected |
| ROB-3 | Unicode name is accepted |
| ROB-4 | Very long name (300 chars) does not crash the field or the page |
| ROB-5 | A controlled double-click on "Next" (Artist Selection step, no tier picked) does not skip past the budget-tier sub-step |

## 9. Navigation and Persistence

| # | Scenario |
|---|---|
| NAV-1 | "Previous" on Event Details returns to Artist Selection |
| NAV-2 | Double-clicking "Next" before a required selection is made does not advance two steps at once |
| NAV-3 | Selected event/location/contact data is still shown correctly on the Review & Pay screen after navigating forward through all steps once |

## 10. Review / Summary

| # | Scenario |
|---|---|
| REV-1 | Booking Summary shows Artist Type, Event, Date & Time, Gender, Event Duration, Artist's Experience, Offers Applied |
| REV-2 | Collapsible "Venue & Contact Details" card shows Contact (name/email/phone, with an "Edit" link) and Venue (full address + condensed City/Pin) |
| REV-3 | Pricing shown in Booking Summary/Offers Applied matches the tier selected in step 1 |
| REV-4 | Two payment options are offered: "Pay Now" (full discounted price, conveyance fee waived) and "Pay Upon Arrival" (higher total, ₹99 reservation fee payable now) |
| REV-5 | A countdown ("Your booking slot is reserved for X:XX") is shown on this step |

## 11. Final Step (safety-bounded)

| # | Scenario |
|---|---|
| FIN-1 | The "SECURELY PAY ₹99" button is present, labelled with the Razorpay-powered trust badges (256-bit SSL, RBI Regulated, 100% Refundable, No Hidden Charges) |
| FIN-2 | Automation **never clicks** this button — this is the deliberate, documented stopping point (see `test_execution_summary.md`) |

## Boundary / Validation data actually used

- Emails: `plainaddress`, `test@`, `@test.com`, `test.com`, `test@domain`, leading/trailing space variants
- Phones: too short (`123`), too long (15 digits), alphabetic, special characters, blank
- Location: exact ("Jaunpur"), partial ("Jaun"), nonsense strings, typed-but-unselected
- Name: Unicode, 300-character string, whitespace-only
