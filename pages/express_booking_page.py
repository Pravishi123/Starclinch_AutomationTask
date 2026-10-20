"""Step 1 of the real /on-demand wizard: 'Artist Selection'.

Covers the Artist Preferences sub-section (artist type, gender preference, event
duration), the 'Choose your booking experience' offer-type radios, and the 'Your
Budget' tier tiles - all three live on this one wizard step in the real application.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from config.config import ON_DEMAND_URL


class ExpressBookingPage(BasePage):
    ARTIST_TYPE_DROPDOWN = (By.CSS_SELECTOR, ".category-dropdown-container")
    GENDER_DROPDOWN = (By.CSS_SELECTOR, ".gender-dropdown-container")
    NEXT_BUTTON = (By.XPATH, "//button[.//text()[contains(., 'Next')]]")
    PICK_OPTION_VALIDATION = (By.XPATH, "//p[contains(text(), 'Please pick an option')]")
    OFFER_RADIOS = (By.CSS_SELECTOR, 'input[name="durationOffer"]')

    @staticmethod
    def _dropdown_option(label: str):
        # Option labels render as <p>Singer<span> (with ...)</span></p>, so the label
        # text is split across child nodes - match on the <p>'s full string value.
        return (By.XPATH, f"//p[normalize-space(.)='{label}']")

    @staticmethod
    def _duration_option(label: str):
        return (By.XPATH, f"//div[contains(text(),'{label}')]")

    @staticmethod
    def _budget_tier(tier_name: str):
        return (
            By.XPATH,
            f"//span[normalize-space(text())='{tier_name}']/ancestor::div[contains(@class,'cursor-pointer')][1]",
        )

    @staticmethod
    def _budget_tier_prices(tier_name: str):
        """Prices sit in sibling <span> text nodes after the tier name span."""
        return (
            By.XPATH,
            f"//span[normalize-space(text())='{tier_name}']"
            "/ancestor::div[contains(@class,'cursor-pointer')][1]"
            "//span[contains(text(),'₹')]",
        )

    def open(self, url: str = ON_DEMAND_URL):
        # This is a client-rendered SPA: document.title is set by JS after hydration,
        # not present in the initial HTML response. Checking driver.title immediately
        # after driver.get() can race that and read "" (observed via a real failed
        # run - see docs/test_execution_summary.md), so wait for it here rather than
        # in every caller.
        super().open(url)
        self.wait.until(lambda d: d.title != "")

    def select_artist_type(self, label: str = "Singer (with Guitar/Instrument/Karaoke)"):
        self.click(self.ARTIST_TYPE_DROPDOWN)
        self.click(self._dropdown_option(label))

    def select_artist_preference(self, label: str = "Male Artist"):
        self.click(self.GENDER_DROPDOWN)
        self.click(self._dropdown_option(label))

    def select_event_duration(self, label: str = "45 mins"):
        self.js_click(self._duration_option(label))

    def select_offer_type(self, new_users_only: bool = True):
        radios = self.find_all(self.OFFER_RADIOS)
        index = 0 if new_users_only else 1
        self.driver.execute_script("arguments[0].click();", radios[index])

    def select_budget_tier(self, tier_name: str = "Value"):
        self.js_click(self._budget_tier(tier_name))

    def get_budget_tier_prices(self, tier_name: str) -> dict:
        spans = self.find_all(self._budget_tier_prices(tier_name))
        prices = [s.text.strip() for s in spans if s.text.strip()]
        return {
            "original_price": prices[0] if len(prices) > 0 else None,
            "discounted_price": prices[1] if len(prices) > 1 else None,
        }

    def get_pick_option_validation_text(self) -> str:
        return self.get_text(self.PICK_OPTION_VALIDATION)

    def has_pick_option_validation(self) -> bool:
        return self.is_visible(self.PICK_OPTION_VALIDATION)

    def click_next(self):
        self.click(self.NEXT_BUTTON)
